"""Coverage Blocker Explanation – P5 core innovation module.

This module answers the question "**Why** are these lines not covered?"
by tracing missing lines/branches back to their **controlling predicates**
(conditions in ``if``, ``match``, ``switch`` statements) and extracting
the predicate text, variables, and a human-readable hint.

The blockers are injected into the LLM prompt so that the model understands
*why* particular code paths are unreachable, not just *which* lines to hit.

Design goals
------------
* Language-agnostic API: ``extract_blockers()`` dispatches to Rust / Go / Python
  extractors internally.
* Small, frozen data classes for JSON serialisation and trace logging.
* ``format_blockers_for_prompt()`` renders a structured "COVERAGE ANALYSIS"
  block ready for prompt injection.
* Graceful degradation: if tree-sitter is unavailable or parsing fails, the
  function returns an empty list (the prompt simply lacks blocker info).
"""

from __future__ import annotations

import ast as python_ast
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ── Data classes ────────────────────────────────────────────────────────

class PredicateKind(str, Enum):
    """Kind of predicate guarding the missing code."""
    IF_CONDITION = "if_condition"
    ELSE_BRANCH = "else_branch"
    MATCH_ARM = "match_arm"
    SWITCH_CASE = "switch_case"
    SELECT_CASE = "select_case"
    LOOP_CONDITION = "loop_condition"
    IF_LET = "if_let"
    DEFAULT_BRANCH = "default_branch"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class VariableOrigin:
    """Where a variable in a predicate comes from."""
    name: str
    origin_kind: str        # "parameter", "field", "local", "return_value", "unknown"
    origin_detail: str = "" # e.g. "fn_name arg #2", "self.field_name"
    type_hint: str = ""     # best-effort type info


@dataclass(frozen=True)
class CoverageBlocker:
    """A single explanation for why a set of lines is not covered.

    Each blocker links a group of missing target lines to the controlling
    predicate that must evaluate differently for those lines to execute.
    """
    target_lines: Tuple[int, ...]       # missing lines guarded by this predicate
    predicate_line: int                 # line of the controlling if/match/switch
    predicate_text: str                 # source text of the condition
    predicate_kind: str = PredicateKind.UNKNOWN.value
    variables: Tuple[VariableOrigin, ...] = ()
    hint: str = ""                      # human-readable explanation
    confidence: float = 1.0             # 0..1, lower if heuristic-based

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["variables"] = [asdict(v) for v in self.variables]
        d["target_lines"] = list(self.target_lines)
        return d


# ── Main API ────────────────────────────────────────────────────────────

def extract_blockers(
    path: Path,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
    language: str,
    *,
    max_blockers: int = 5,
) -> List[CoverageBlocker]:
    """Extract coverage blockers for a code segment.

    Dispatches to language-specific extractors.  Returns up to
    *max_blockers* blockers sorted by number of target lines (most
    impactful first).

    Parameters
    ----------
    path : Path
        Source file path.
    missing_lines : set of int
        Lines that should execute but don't.
    missing_branches : set of (int, int)
        Missing branch pairs ``(from_line, to_line)``.
    executed_lines : set of int
        Lines that are already covered.
    language : str
        ``"rust"`` | ``"go"`` | ``"python"``
    max_blockers : int
        Maximum number of blockers to return.
    """
    if not missing_lines and not missing_branches:
        return []

    try:
        if language == "rust":
            blockers = _extract_rust_blockers(
                path, missing_lines, missing_branches, executed_lines
            )
        elif language == "go":
            blockers = _extract_go_blockers(
                path, missing_lines, missing_branches, executed_lines
            )
        elif language == "python":
            blockers = _extract_python_blockers(
                path, missing_lines, missing_branches, executed_lines
            )
        else:
            return []
    except Exception:
        # Graceful degradation: any parse/analysis error → empty list
        return []

    # Sort by impact (most target lines first), then deduplicate
    blockers.sort(key=lambda b: len(b.target_lines), reverse=True)
    return blockers[:max_blockers]


def format_blockers_for_prompt(
    blockers: List[CoverageBlocker],
    *,
    max_chars: int = 1500,
) -> str:
    """Render blockers as a structured prompt block.

    Returns an empty string if there are no blockers.
    """
    if not blockers:
        return ""

    lines = ["COVERAGE ANALYSIS — Why these lines are not reached:"]
    total_len = len(lines[0])

    for i, b in enumerate(blockers, 1):
        target_str = _format_line_ranges(sorted(b.target_lines))
        kind_label = b.predicate_kind.replace("_", " ")

        entry = (
            f"  {i}. Lines {target_str} are blocked by {kind_label} "
            f"at line {b.predicate_line}: `{b.predicate_text}`"
        )

        if b.hint:
            entry += f"\n     Hint: {b.hint}"

        if b.variables:
            var_descs = []
            for v in b.variables:
                desc = f"`{v.name}`"
                if v.type_hint:
                    desc += f" ({v.type_hint})"
                if v.origin_detail:
                    desc += f" — {v.origin_detail}"
                var_descs.append(desc)
            entry += f"\n     Key variables: {', '.join(var_descs)}"

        if total_len + len(entry) > max_chars:
            lines.append(f"  ... ({len(blockers) - i + 1} more blockers omitted)")
            break

        lines.append(entry)
        total_len += len(entry)

    return "\n".join(lines)


# ── Rust extractor ──────────────────────────────────────────────────────

def _extract_rust_blockers(
    path: Path,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
) -> List[CoverageBlocker]:
    """Extract blockers from Rust source using tree-sitter."""
    try:
        from tree_sitter import Parser
        from tree_sitter_languages import get_language
    except ImportError:
        return []

    parser = Parser()
    parser.set_language(get_language("rust"))

    try:
        source = path.read_bytes()
    except OSError:
        return []

    tree = parser.parse(source)
    blockers: List[CoverageBlocker] = []

    for node in _ts_walk(tree.root_node):
        if node.type in ("if_expression", "if_let_expression"):
            _rust_analyze_if_blocker(
                node, source, missing_lines, missing_branches,
                executed_lines, blockers
            )
        elif node.type == "match_expression":
            _rust_analyze_match_blocker(
                node, source, missing_lines, missing_branches,
                executed_lines, blockers
            )

    return blockers


def _rust_analyze_if_blocker(
    node, source: bytes,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
    blockers: List[CoverageBlocker],
):
    """Analyze an if/if-let for blocker information."""
    cond_line = node.start_point[0] + 1

    # Extract condition text
    condition = node.child_by_field_name("condition")
    if condition:
        cond_text = _ts_node_text(condition, source)
    else:
        # For if_let, the whole line is the condition
        cond_text = _ts_node_text(node, source).split("{")[0].strip()

    consequence = node.child_by_field_name("consequence")
    alternative = node.child_by_field_name("alternative")

    # Check if the true branch is missing
    if consequence:
        target = _collect_missing_in_block(consequence, missing_lines)
        if target:
            kind = (PredicateKind.IF_LET.value
                    if node.type == "if_let_expression"
                    else PredicateKind.IF_CONDITION.value)
            variables = _extract_variables_from_text(cond_text)
            hint = _generate_if_hint(cond_text, is_true_branch=True)
            blockers.append(CoverageBlocker(
                target_lines=tuple(sorted(target)),
                predicate_line=cond_line,
                predicate_text=_truncate(cond_text, 120),
                predicate_kind=kind,
                variables=tuple(variables),
                hint=hint,
            ))

    # Check if the else/else-if branch is missing
    if alternative:
        target = _collect_missing_in_block(alternative, missing_lines)
        if target:
            variables = _extract_variables_from_text(cond_text)
            hint = _generate_if_hint(cond_text, is_true_branch=False)
            blockers.append(CoverageBlocker(
                target_lines=tuple(sorted(target)),
                predicate_line=cond_line,
                predicate_text=_truncate(cond_text, 120),
                predicate_kind=PredicateKind.ELSE_BRANCH.value,
                variables=tuple(variables),
                hint=hint,
            ))
    elif not alternative:
        # Implicit else: if condition is always true, the code after if never runs
        # Check if any missing lines are right after the if block
        pass  # TODO: track implicit else blockers


def _rust_analyze_match_blocker(
    node, source: bytes,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
    blockers: List[CoverageBlocker],
):
    """Analyze match expression arms for blocker information."""
    match_line = node.start_point[0] + 1

    # Extract the match value expression
    value = node.child_by_field_name("value")
    value_text = _ts_node_text(value, source) if value else "?"

    body = node.child_by_field_name("body")
    if not body:
        return

    for child in body.children:
        if child.type == "match_arm":
            pattern = child.child_by_field_name("pattern")
            arm_value = child.child_by_field_name("value")
            if arm_value:
                target = _collect_missing_in_node(arm_value, missing_lines)
                if target:
                    pattern_text = _ts_node_text(pattern, source) if pattern else "?"
                    cond_text = f"match {value_text} => {pattern_text}"
                    variables = _extract_variables_from_text(value_text)
                    blockers.append(CoverageBlocker(
                        target_lines=tuple(sorted(target)),
                        predicate_line=match_line,
                        predicate_text=_truncate(cond_text, 120),
                        predicate_kind=PredicateKind.MATCH_ARM.value,
                        variables=tuple(variables),
                        hint=f"Need `{value_text}` to match pattern `{_truncate(pattern_text, 60)}`",
                    ))


# ── Go extractor ────────────────────────────────────────────────────────

def _extract_go_blockers(
    path: Path,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
) -> List[CoverageBlocker]:
    """Extract blockers from Go source using tree-sitter."""
    try:
        from tree_sitter import Parser
        from tree_sitter_languages import get_language
    except ImportError:
        return []

    parser = Parser()
    parser.set_language(get_language("go"))

    try:
        source = path.read_bytes()
    except OSError:
        return []

    tree = parser.parse(source)
    blockers: List[CoverageBlocker] = []

    for node in _ts_walk(tree.root_node):
        if node.type == "if_statement":
            _go_analyze_if_blocker(
                node, source, missing_lines, missing_branches,
                executed_lines, blockers
            )
        elif node.type in ("expression_switch_statement", "type_switch_statement"):
            _go_analyze_switch_blocker(
                node, source, missing_lines, missing_branches,
                executed_lines, blockers
            )
        elif node.type == "select_statement":
            _go_analyze_select_blocker(
                node, source, missing_lines, executed_lines, blockers
            )

    return blockers


def _go_analyze_if_blocker(
    node, source: bytes,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
    blockers: List[CoverageBlocker],
):
    """Analyze a Go if statement for blocker information."""
    cond_line = node.start_point[0] + 1

    condition = node.child_by_field_name("condition")
    cond_text = _ts_node_text(condition, source) if condition else "?"

    consequence = node.child_by_field_name("consequence")
    alternative = node.child_by_field_name("alternative")

    if consequence:
        target = _collect_missing_in_block(consequence, missing_lines)
        if target:
            variables = _extract_variables_from_text(cond_text)
            hint = _generate_if_hint(cond_text, is_true_branch=True)
            blockers.append(CoverageBlocker(
                target_lines=tuple(sorted(target)),
                predicate_line=cond_line,
                predicate_text=_truncate(cond_text, 120),
                predicate_kind=PredicateKind.IF_CONDITION.value,
                variables=tuple(variables),
                hint=hint,
            ))

    if alternative:
        target = _collect_missing_in_block(alternative, missing_lines)
        if target:
            variables = _extract_variables_from_text(cond_text)
            hint = _generate_if_hint(cond_text, is_true_branch=False)
            blockers.append(CoverageBlocker(
                target_lines=tuple(sorted(target)),
                predicate_line=cond_line,
                predicate_text=_truncate(cond_text, 120),
                predicate_kind=PredicateKind.ELSE_BRANCH.value,
                variables=tuple(variables),
                hint=hint,
            ))


def _go_analyze_switch_blocker(
    node, source: bytes,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
    blockers: List[CoverageBlocker],
):
    """Analyze Go switch statement for blocker information."""
    switch_line = node.start_point[0] + 1

    # Try to get the switch value
    value_node = node.child_by_field_name("value")
    value_text = _ts_node_text(value_node, source) if value_node else "?"

    for child in _ts_walk(node):
        if child.type in ("expression_case", "type_case"):
            target = _collect_missing_in_node(child, missing_lines)
            if target:
                # Extract case expression
                case_exprs = []
                for sub in child.children:
                    if sub.type == "expression_list":
                        case_exprs.append(_ts_node_text(sub, source))
                case_text = ", ".join(case_exprs) if case_exprs else "?"
                cond_text = f"switch {value_text} case {case_text}"
                variables = _extract_variables_from_text(value_text)
                blockers.append(CoverageBlocker(
                    target_lines=tuple(sorted(target)),
                    predicate_line=switch_line,
                    predicate_text=_truncate(cond_text, 120),
                    predicate_kind=PredicateKind.SWITCH_CASE.value,
                    variables=tuple(variables),
                    hint=f"Need `{value_text}` to equal `{_truncate(case_text, 60)}`",
                ))
        elif child.type == "default_case":
            target = _collect_missing_in_node(child, missing_lines)
            if target:
                blockers.append(CoverageBlocker(
                    target_lines=tuple(sorted(target)),
                    predicate_line=switch_line,
                    predicate_text=f"switch {value_text} default",
                    predicate_kind=PredicateKind.DEFAULT_BRANCH.value,
                    variables=tuple(_extract_variables_from_text(value_text)),
                    hint=f"Need `{value_text}` to not match any case",
                ))


def _go_analyze_select_blocker(
    node, source: bytes,
    missing_lines: Set[int],
    executed_lines: Set[int],
    blockers: List[CoverageBlocker],
):
    """Analyze Go select statement for blocker information."""
    select_line = node.start_point[0] + 1

    for child in _ts_walk(node):
        if child.type == "communication_case":
            target = _collect_missing_in_node(child, missing_lines)
            if target:
                # Get channel operation text
                comm_text = "?"
                for sub in child.children:
                    if sub.type not in ("case", ":", "comment"):
                        comm_text = _ts_node_text(sub, source)
                        break
                blockers.append(CoverageBlocker(
                    target_lines=tuple(sorted(target)),
                    predicate_line=select_line,
                    predicate_text=_truncate(f"select {comm_text}", 120),
                    predicate_kind=PredicateKind.SELECT_CASE.value,
                    hint=f"Need channel operation `{_truncate(comm_text, 60)}` to be ready",
                ))


# ── Python extractor ───────────────────────────────────────────────────

def _extract_python_blockers(
    path: Path,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
) -> List[CoverageBlocker]:
    """Extract blockers from Python source using stdlib ast."""
    try:
        source_text = path.read_text()
    except OSError:
        return []

    try:
        tree = python_ast.parse(source_text)
    except SyntaxError:
        return []

    source_lines = source_text.splitlines()
    blockers: List[CoverageBlocker] = []

    for node in python_ast.walk(tree):
        if isinstance(node, python_ast.If):
            _python_analyze_if_blocker(
                node, source_lines, missing_lines, executed_lines, blockers
            )
        elif isinstance(node, python_ast.Match):
            _python_analyze_match_blocker(
                node, source_lines, missing_lines, executed_lines, blockers
            )

    return blockers


def _python_analyze_if_blocker(
    node: python_ast.If,
    source_lines: List[str],
    missing_lines: Set[int],
    executed_lines: Set[int],
    blockers: List[CoverageBlocker],
):
    """Analyze a Python if statement for blocker information."""
    cond_line = node.lineno
    cond_text = python_ast.unparse(node.test)

    # True branch (body)
    body_missing = {
        n.lineno for n in python_ast.walk(python_ast.Module(body=node.body, type_ignores=[]))
        if hasattr(n, 'lineno') and n.lineno in missing_lines
    }
    if not body_missing:
        # Simpler: check line ranges
        body_missing = set()
        for child in node.body:
            end = getattr(child, 'end_lineno', child.lineno)
            for ln in range(child.lineno, end + 1):
                if ln in missing_lines:
                    body_missing.add(ln)

    if body_missing:
        variables = _extract_variables_from_text(cond_text)
        hint = _generate_if_hint(cond_text, is_true_branch=True)
        blockers.append(CoverageBlocker(
            target_lines=tuple(sorted(body_missing)),
            predicate_line=cond_line,
            predicate_text=_truncate(cond_text, 120),
            predicate_kind=PredicateKind.IF_CONDITION.value,
            variables=tuple(variables),
            hint=hint,
        ))

    # Else branch (orelse)
    if node.orelse:
        else_missing = set()
        for child in node.orelse:
            end = getattr(child, 'end_lineno', child.lineno)
            for ln in range(child.lineno, end + 1):
                if ln in missing_lines:
                    else_missing.add(ln)
        if else_missing:
            variables = _extract_variables_from_text(cond_text)
            hint = _generate_if_hint(cond_text, is_true_branch=False)
            blockers.append(CoverageBlocker(
                target_lines=tuple(sorted(else_missing)),
                predicate_line=cond_line,
                predicate_text=_truncate(cond_text, 120),
                predicate_kind=PredicateKind.ELSE_BRANCH.value,
                variables=tuple(variables),
                hint=hint,
            ))


def _python_analyze_match_blocker(
    node: python_ast.Match,
    source_lines: List[str],
    missing_lines: Set[int],
    executed_lines: Set[int],
    blockers: List[CoverageBlocker],
):
    """Analyze a Python match/case statement for blocker information."""
    match_line = node.lineno
    subject_text = python_ast.unparse(node.subject)

    for case in node.cases:
        case_missing = set()
        for child in case.body:
            end = getattr(child, 'end_lineno', child.lineno)
            for ln in range(child.lineno, end + 1):
                if ln in missing_lines:
                    case_missing.add(ln)
        if case_missing:
            pattern_text = python_ast.unparse(case.pattern)
            cond_text = f"match {subject_text} case {pattern_text}"
            variables = _extract_variables_from_text(subject_text)
            blockers.append(CoverageBlocker(
                target_lines=tuple(sorted(case_missing)),
                predicate_line=match_line,
                predicate_text=_truncate(cond_text, 120),
                predicate_kind=PredicateKind.MATCH_ARM.value,
                variables=tuple(variables),
                hint=f"Need `{subject_text}` to match pattern `{_truncate(pattern_text, 60)}`",
            ))


# ── Shared helpers ──────────────────────────────────────────────────────

def _ts_walk(node):
    """Yield node and all descendants (pre-order) for tree-sitter nodes."""
    yield node
    for child in node.children:
        yield from _ts_walk(child)


def _ts_node_text(node, source: bytes) -> str:
    """Extract UTF-8 text of a tree-sitter node."""
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _collect_missing_in_block(block_node, missing_lines: Set[int]) -> Set[int]:
    """Collect missing lines inside a tree-sitter block node."""
    result = set()
    start = block_node.start_point[0] + 1  # 1-based
    end = block_node.end_point[0] + 1
    for ln in range(start, end + 1):
        if ln in missing_lines:
            result.add(ln)
    return result


def _collect_missing_in_node(node, missing_lines: Set[int]) -> Set[int]:
    """Collect missing lines in any tree-sitter node's range."""
    result = set()
    start = node.start_point[0] + 1
    end = node.end_point[0] + 1
    for ln in range(start, end + 1):
        if ln in missing_lines:
            result.add(ln)
    return result


def _extract_variables_from_text(text: str) -> List[VariableOrigin]:
    """Extract variable-like identifiers from predicate text (heuristic).

    This is a best-effort regex-based extraction.  Language-specific
    extractors can override with AST-based analysis for better accuracy.
    """
    # Match identifiers but exclude keywords and literals
    _KEYWORDS = {
        # Rust
        "if", "else", "match", "let", "mut", "fn", "pub", "self", "Self",
        "true", "false", "None", "Some", "Ok", "Err", "return", "break",
        "continue", "as", "in", "for", "while", "loop", "impl", "struct",
        "enum", "trait", "type", "where", "use", "mod", "crate", "super",
        "const", "static", "ref", "move", "async", "await", "dyn", "unsafe",
        # Go
        "func", "var", "package", "import", "defer", "go", "select",
        "chan", "map", "range", "switch", "case", "default", "fallthrough",
        "nil", "iota", "append", "len", "cap", "make", "new", "delete",
        "close", "copy", "panic", "recover", "print", "println",
        "int", "int8", "int16", "int32", "int64",
        "uint", "uint8", "uint16", "uint32", "uint64",
        "float32", "float64", "complex64", "complex128",
        "bool", "byte", "rune", "string", "error", "interface",
        # Python
        "and", "or", "not", "is", "isinstance", "hasattr", "getattr",
        "class", "def", "del", "with", "try", "except", "finally",
        "raise", "yield", "from", "global", "nonlocal", "assert",
        "pass", "lambda", "True", "False",
    }

    idents = re.findall(r'\b([a-zA-Z_]\w*)\b', text)
    seen = set()
    result = []
    for ident in idents:
        if ident in _KEYWORDS or ident in seen:
            continue
        if len(ident) <= 1 and ident not in ("x", "n", "i", "s"):
            continue
        seen.add(ident)
        result.append(VariableOrigin(
            name=ident,
            origin_kind="unknown",
        ))
    return result


def _generate_if_hint(cond_text: str, is_true_branch: bool) -> str:
    """Generate a human-readable hint for an if/else blocker."""
    cond_short = _truncate(cond_text, 80)
    if is_true_branch:
        return f"Need condition `{cond_short}` to be TRUE"
    else:
        return f"Need condition `{cond_short}` to be FALSE"


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis if too long."""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def _format_line_ranges(lines: List[int]) -> str:
    """Format a list of line numbers as compact ranges (e.g. '10-12, 15')."""
    if not lines:
        return ""
    ranges = []
    start = prev = lines[0]
    for ln in lines[1:]:
        if ln == prev + 1:
            prev = ln
        else:
            ranges.append(f"{start}-{prev}" if start != prev else str(start))
            start = prev = ln
    ranges.append(f"{start}-{prev}" if start != prev else str(start))
    return ", ".join(ranges)
