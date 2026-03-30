"""Static analysis utilities for Go source code using tree-sitter.

This module provides functionality analogous to ``codeinfo.py`` (which targets
Python via the ``ast`` module), but for Go source files.  It powers the
``get_info`` tool function exposed to the LLM when generating Go tests and
supplies additional helpers used by the Go backend for richer code context.
"""

import os
import re
import subprocess
import typing as T
from pathlib import Path


# ---------------------------------------------------------------------------
# tree-sitter bootstrap
# ---------------------------------------------------------------------------

_parser = None


def _ensure_parser():
    global _parser
    if _parser is not None:
        return _parser
    try:
        from tree_sitter import Parser  # type: ignore[import-not-found]
        from tree_sitter_languages import get_language  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "Go code analysis requires 'tree_sitter' and 'tree_sitter_languages' packages"
        ) from exc
    _parser = Parser()
    _parser.set_language(get_language("go"))
    return _parser


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _node_text(node, source: bytes) -> str:
    """Extract the UTF-8 text of a tree-sitter node."""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _walk(node):
    """Yield *node* and all of its descendants (pre-order)."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _iter_top_level(root):
    """Yield the immediate children of the root that are declarations."""
    for child in root.children:
        yield child


# ---------------------------------------------------------------------------
# Symbol finders
# ---------------------------------------------------------------------------

def _find_function_decl(root, source: bytes, name: str):
    """Find a top-level ``func <name>(…)`` declaration."""
    for child in root.children:
        if child.type == "function_declaration":
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


def _find_method_decl(root, source: bytes, receiver_type: str, method_name: str):
    """Find ``func (r <receiver_type>) <method_name>(…)``."""
    for child in root.children:
        if child.type == "method_declaration":
            mn = child.child_by_field_name("name")
            if mn and _node_text(mn, source) == method_name:
                recv = child.child_by_field_name("receiver")
                if recv and receiver_type in _node_text(recv, source):
                    return child
    return None


def _find_type_spec(root, source: bytes, name: str):
    """Find a ``type <name> struct/interface { … }`` inside a type_declaration."""
    for child in root.children:
        if child.type == "type_declaration":
            for spec in child.children:
                if spec.type == "type_spec":
                    n = spec.child_by_field_name("name")
                    if n and _node_text(n, source) == name:
                        return spec
    return None


def _find_const_or_var(root, source: bytes, name: str):
    """Find a top-level ``const`` or ``var`` declaration containing *name*."""
    for child in root.children:
        if child.type in ("const_declaration", "var_declaration"):
            text = _node_text(child, source)
            # Quick textual check – we look for the identifier
            if re.search(rf'\b{re.escape(name)}\b', text):
                return child
    return None


# ---------------------------------------------------------------------------
# Collecting all methods for a type across a package
# ---------------------------------------------------------------------------

def _collect_methods_for_type(
    package_dir: Path, type_name: str, *, exclude_file: Path | None = None
) -> list[str]:
    """Return source text of all method declarations whose receiver is *type_name*."""
    parser = _ensure_parser()
    methods: list[str] = []
    for go_file in sorted(package_dir.glob("*.go")):
        if go_file.name.endswith("_test.go"):
            continue
        if exclude_file and go_file.resolve() == exclude_file.resolve():
            continue
        try:
            src = go_file.read_bytes()
        except OSError:
            continue
        tree = parser.parse(src)
        for child in tree.root_node.children:
            if child.type == "method_declaration":
                recv = child.child_by_field_name("receiver")
                if recv and type_name in _node_text(recv, src):
                    methods.append(_node_text(child, src))
    return methods


# ---------------------------------------------------------------------------
# Public: get_info for Go
# ---------------------------------------------------------------------------

def get_info_go(
    file_path: Path,
    name: str,
    *,
    module_root: Path | None = None,
    line: int = 0,
) -> str | None:
    """Return summarized information about Go symbol *name*.

    Supports the following forms of *name*:
    - ``FuncName``          – top-level function
    - ``TypeName``          – struct / interface definition (+ constructor if present)
    - ``TypeName.Method``   – method on a type
    - ``packageName.Symbol``– looks up in sibling package (best-effort via ``go doc``)

    Returns a string suitable for inclusion in LLM context, or ``None`` if the
    symbol cannot be found.
    """
    parser = _ensure_parser()
    try:
        source = file_path.read_bytes()
    except OSError:
        return None

    tree = parser.parse(source)
    root = tree.root_node

    parts = name.split(".")

    # ---- Case 1: simple name (function, type, const/var) ----
    if len(parts) == 1:
        sym = parts[0]

        # function?
        node = _find_function_decl(root, source, sym)
        if node:
            return _format_go_snippet(node, source, file_path)

        # type?
        node = _find_type_spec(root, source, sym)
        if node:
            result = _format_go_type_with_methods(node, source, file_path)
            return result

        # const / var?
        node = _find_const_or_var(root, source, sym)
        if node:
            return _format_go_snippet(node, source, file_path)

        # try same-package files
        return _search_package(file_path.parent, sym, exclude=file_path)

    # ---- Case 2: Type.Method ----
    if len(parts) == 2:
        type_name, method_name = parts

        # Direct method in this file
        node = _find_method_decl(root, source, type_name, method_name)
        if node:
            return _format_go_snippet(node, source, file_path)

        # Search same-package files for method
        result = _search_package_method(file_path.parent, type_name, method_name)
        if result:
            return result

        # Maybe parts[0] is a *package* name  – try go doc
        return _try_go_doc(name, module_root or file_path.parent)

    # ---- Case 3: package.Type.Method or longer ----
    return _try_go_doc(name, module_root or file_path.parent)


# ---------------------------------------------------------------------------
# Intra-package search
# ---------------------------------------------------------------------------

def _search_package(package_dir: Path, name: str, *, exclude: Path | None = None) -> str | None:
    """Search all non-test ``.go`` files in *package_dir* for *name*."""
    parser = _ensure_parser()
    for go_file in sorted(package_dir.glob("*.go")):
        if go_file.name.endswith("_test.go"):
            continue
        if exclude and go_file.resolve() == exclude.resolve():
            continue
        try:
            src = go_file.read_bytes()
        except OSError:
            continue
        tree = parser.parse(src)
        root = tree.root_node

        node = _find_function_decl(root, src, name)
        if node:
            return _format_go_snippet(node, src, go_file)

        node = _find_type_spec(root, src, name)
        if node:
            return _format_go_type_with_methods(node, src, go_file)

        node = _find_const_or_var(root, src, name)
        if node:
            return _format_go_snippet(node, src, go_file)

    return None


def _search_package_method(package_dir: Path, type_name: str, method_name: str) -> str | None:
    parser = _ensure_parser()
    for go_file in sorted(package_dir.glob("*.go")):
        if go_file.name.endswith("_test.go"):
            continue
        try:
            src = go_file.read_bytes()
        except OSError:
            continue
        tree = parser.parse(src)
        node = _find_method_decl(tree.root_node, src, type_name, method_name)
        if node:
            return _format_go_snippet(node, src, go_file)
    return None


# ---------------------------------------------------------------------------
# go doc fallback
# ---------------------------------------------------------------------------

def _try_go_doc(name: str, cwd: Path) -> str | None:
    """Use ``go doc`` as a fallback for cross-package symbols."""
    try:
        result = subprocess.run(
            ["go", "doc", name],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            text = result.stdout.strip()
            # Truncate if too long
            if len(text) > 3000:
                text = text[:3000] + "\n// ... (truncated)"
            return f"From `go doc {name}`:\n```go\n{text}\n```"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_go_snippet(node, source: bytes, file_path: Path) -> str:
    """Format a single tree-sitter node as a Go code snippet."""
    text = _node_text(node, source)
    rel = file_path.name
    return f"in {rel}:\n```go\n{text}\n```"


def _format_go_type_with_methods(
    type_spec_node, source: bytes, file_path: Path, *, max_methods: int = 10
) -> str:
    """Format a type definition together with a summary of its methods."""
    type_text = _node_text(type_spec_node, source)
    name_node = type_spec_node.child_by_field_name("name")
    type_name = _node_text(name_node, source) if name_node else None

    result = f"in {file_path.name}:\n```go\ntype {type_text}\n```"

    if type_name:
        methods = _collect_methods_for_type(file_path.parent, type_name)
        if methods:
            shown = methods[:max_methods]
            sigs: list[str] = []
            for m in shown:
                # Extract just the signature line (first line of func declaration)
                sig_line = m.split("{")[0].strip()
                sigs.append(sig_line)

            result += "\n\nMethods:\n```go\n" + "\n".join(sigs)
            if len(methods) > max_methods:
                result += f"\n// ... and {len(methods) - max_methods} more methods"
            result += "\n```"

    return result


# ---------------------------------------------------------------------------
# Receiver type extraction (used by go_backend for context)
# ---------------------------------------------------------------------------

def extract_receiver_type(node, source: bytes) -> str | None:
    """Given a method_declaration node, return the receiver's type name (without pointer)."""
    recv = node.child_by_field_name("receiver")
    if recv is None:
        return None
    recv_text = _node_text(recv, source)
    # (r *Type) or (r Type) → extract Type
    match = re.search(r'\*?([A-Z]\w*)', recv_text)
    return match.group(1) if match else None


def find_type_definition(root, source: bytes, type_name: str) -> str | None:
    """Find and return the source text of a type definition."""
    spec = _find_type_spec(root, source, type_name)
    if spec:
        # Include the 'type' keyword
        parent = spec.parent
        if parent and parent.type == "type_declaration":
            return _node_text(parent, source)
        return "type " + _node_text(spec, source)
    return None


# ---------------------------------------------------------------------------
# Control-flow analysis for branch inference
# ---------------------------------------------------------------------------

def find_control_flow_nodes(root):
    """Yield (node_type, node) for every control-flow statement in the AST."""
    for node in _walk(root):
        if node.type in (
            "if_statement",
            "expression_switch_statement",
            "type_switch_statement",
            "select_statement",
            "for_statement",
        ):
            yield node


def infer_branches(
    path: Path,
    executed_lines: set[int],
    missing_lines: set[int],
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Infer executed and missing branches from control-flow + line coverage.

    Returns ``(executed_branches, missing_branches)`` where each branch is
    ``(from_line, to_line)`` with ``to_line == 0`` meaning "exit".
    """
    parser = _ensure_parser()
    try:
        source = path.read_bytes()
    except OSError:
        return [], []

    tree = parser.parse(source)
    executed_branches: list[tuple[int, int]] = []
    missing_branches: list[tuple[int, int]] = []

    for node in find_control_flow_nodes(tree.root_node):
        if node.type == "if_statement":
            _analyze_if(node, source, executed_lines, missing_lines,
                        executed_branches, missing_branches)
        elif node.type in ("expression_switch_statement", "type_switch_statement"):
            _analyze_switch(node, source, executed_lines, missing_lines,
                            executed_branches, missing_branches)
        elif node.type == "select_statement":
            _analyze_select(node, source, executed_lines, missing_lines,
                            executed_branches, missing_branches)

    return executed_branches, missing_branches


def _first_body_line(node, source: bytes) -> int:
    """Return the 1-based line of the first statement inside a block."""
    block = node.child_by_field_name("body") or node.child_by_field_name("consequence")
    if block is None:
        # For some switch cases, the body is directly in children
        for child in node.children:
            if child.type == "block":
                block = child
                break
    if block:
        for child in block.children:
            if child.type not in ("{", "}", "comment"):
                return child.start_point[0] + 1
    return node.start_point[0] + 1


def _analyze_if(node, source, executed_lines, missing_lines,
                exec_br, miss_br):
    """Analyze an if / if-else to detect branch coverage."""
    cond_line = node.start_point[0] + 1

    consequence = node.child_by_field_name("consequence")
    alternative = node.child_by_field_name("alternative")

    if consequence:
        first_line = _first_body_line_of_block(consequence)
        if first_line:
            branch = (cond_line, first_line)
            if first_line in executed_lines:
                exec_br.append(branch)
            elif first_line in missing_lines:
                miss_br.append(branch)

    if alternative:
        first_line = _first_body_line_of_block(alternative)
        if first_line:
            branch = (cond_line, first_line)
            if first_line in executed_lines:
                exec_br.append(branch)
            elif first_line in missing_lines:
                miss_br.append(branch)
    else:
        # no else → the "false" branch falls through (exit from if)
        end_line = node.end_point[0] + 2  # line after the if block
        branch = (cond_line, 0)  # 0 = exit
        # If the if-body was executed but there's code after the if that also executed,
        # we assume the false branch was taken somewhere; otherwise mark missing
        if consequence:
            body_lines = set(range(consequence.start_point[0] + 1, consequence.end_point[0] + 2))
            if body_lines & executed_lines and not (body_lines & missing_lines):
                # True branch fully executed – we can't tell about false from line coverage alone
                pass
            elif body_lines & missing_lines:
                # True branch has missing lines; false branch unknown
                pass


def _first_body_line_of_block(block_node) -> int | None:
    """Return first meaningful line inside a block node."""
    for child in block_node.children:
        if child.type not in ("{", "}", "comment", "\n"):
            return child.start_point[0] + 1
    return None


def _analyze_switch(node, source, executed_lines, missing_lines, exec_br, miss_br):
    """Analyze switch/case branches."""
    switch_line = node.start_point[0] + 1
    for child in _walk(node):
        if child.type in ("expression_case", "type_case", "default_case"):
            first_line = None
            for stmt in child.children:
                if stmt.type not in ("case", "default", ":", "expression_list", "type_list", "comment"):
                    first_line = stmt.start_point[0] + 1
                    break
            if first_line:
                branch = (switch_line, first_line)
                if first_line in executed_lines:
                    exec_br.append(branch)
                elif first_line in missing_lines:
                    miss_br.append(branch)


def _analyze_select(node, source, executed_lines, missing_lines, exec_br, miss_br):
    """Analyze select/case branches (channel operations)."""
    select_line = node.start_point[0] + 1
    for child in _walk(node):
        if child.type == "communication_case":
            first_line = None
            for stmt in child.children:
                if stmt.type not in ("case", "default", ":", "<-", "comment"):
                    first_line = stmt.start_point[0] + 1
                    break
            if first_line:
                branch = (select_line, first_line)
                if first_line in executed_lines:
                    exec_br.append(branch)
                elif first_line in missing_lines:
                    miss_br.append(branch)
