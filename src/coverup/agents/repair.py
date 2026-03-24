"""Repair Orchestrator – two-phase repair: tool-first then LLM fallback.

Phase 1 (deterministic / tool-first):
    Apply cheap, high-confidence pattern-based fixes that do not require
    an LLM call.  Examples: add missing ``use`` in Rust, add missing
    ``import`` in Python, run ``goimports`` for Go.

Phase 2 (LLM fallback):
    If Phase 1 does not fully resolve the compilation error, the
    formatted error + Diagnostic IR is passed back to the LLM via the
    existing ``error_prompt`` flow.

The orchestrator is language-agnostic: language-specific fix functions
are registered per ``(language, error_category)`` pair.

Design
------
* ``RepairOrchestrator`` holds a registry of ``FixFunc`` callables.
* Each ``FixFunc`` receives ``(test_code, DiagnosticIR, backend)`` and
  returns ``(patched_code, list_of_applied_fix_names)``.
* The core loop in ``coverup.py`` calls ``orchestrator.try_tool_repair()``
  *before* falling back to the LLM error prompt.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..diagnostic_ir import DiagnosticIR, ErrorCategory


# Type alias for a fix function
FixFunc = Callable[
    [str, DiagnosticIR, Any],          # (test_code, ir, backend)
    Tuple[str, List[str]],             # (patched_code, applied_fix_names)
]


class RepairOrchestrator:
    """Manages deterministic repair patterns across languages.

    Usage::

        repair = RepairOrchestrator()
        patched, fixes = repair.try_tool_repair(test_code, ir, backend)
        if fixes:
            # re-verify patched code without an LLM call
            ...
        else:
            # fall back to LLM error_prompt
            ...
    """

    def __init__(self) -> None:
        # Registry: (language, error_category) → list of fix functions
        self._registry: Dict[Tuple[str, str], List[FixFunc]] = {}
        # Register built-in fixers
        self._register_defaults()

    def register(self, language: str, category: str, func: FixFunc) -> None:
        """Register a fix function for a (language, category) pair."""
        key = (language, category)
        self._registry.setdefault(key, []).append(func)

    def try_tool_repair(
        self,
        test_code: str,
        ir: DiagnosticIR,
        backend: Any,
    ) -> Tuple[str, List[str]]:
        """Attempt all registered tool-first repairs.

        Returns ``(patched_code, applied_fix_names)``.
        If no fixes applied, returns ``(test_code, [])``.
        """
        key = (ir.language, ir.error_category)
        fixers = self._registry.get(key, [])

        all_applied: List[str] = []
        current = test_code

        for fixer in fixers:
            try:
                patched, names = fixer(current, ir, backend)
                if names:
                    current = patched
                    all_applied.extend(names)
            except Exception as exc:
                # Fixer crashed — skip it but log for debugging
                import logging
                logging.debug(f"Fixer {fixer.__name__} crashed: {exc}")
                continue

        # Also try generic fixers (any category)
        generic_key = (ir.language, "*")
        for fixer in self._registry.get(generic_key, []):
            try:
                patched, names = fixer(current, ir, backend)
                if names:
                    current = patched
                    all_applied.extend(names)
            except Exception:
                continue

        return current, all_applied

    def available_fixers(self, language: str) -> List[str]:
        """List registered fix categories for a language."""
        cats = set()
        for (lang, cat) in self._registry:
            if lang == language:
                cats.add(cat)
        return sorted(cats)

    # ── Default fixers ──────────────────────────────────────────────

    def _register_defaults(self) -> None:
        """Register all built-in language-specific fixers."""

        # ---- Rust ----
        self.register("rust", ErrorCategory.IMPORT.value, _rust_fix_imports)
        # NOTE: _rust_fix_type_hints and _rust_fix_visibility are stubs (no-op)
        # and not registered until they have real implementations.
        # Cargo-check structured autofix (applies MachineApplicable suggestions)
        self.register("rust", "*", _rust_cargo_check_autofix)

        # ---- Python ----
        self.register("python", ErrorCategory.IMPORT.value, _python_fix_imports)
        self.register("python", ErrorCategory.SYNTAX.value, _python_fix_syntax)

        # ---- Go ----
        self.register("go", ErrorCategory.IMPORT.value, _go_fix_imports)


# ====================================================================
# Built-in fix functions
# ====================================================================

# ---- Rust fixers ---------------------------------------------------

def _rust_fix_imports(
    test_code: str, ir: DiagnosticIR, backend: Any
) -> Tuple[str, List[str]]:
    """Fix missing Rust imports using the backend's item_module_lookup."""
    applied: List[str] = []

    # Delegate to backend's _autofix_submodule_imports if available
    if hasattr(backend, '_autofix_submodule_imports') and hasattr(backend, '_crate_name'):
        crate_name = backend._crate_name or "crate"
        fixed = backend._autofix_submodule_imports(test_code, crate_name)
        if fixed != test_code:
            applied.append("rust_autofix_submodule_imports")
            test_code = fixed

    # Additional: fix "cannot find X in this scope" by adding explicit imports
    lookup = getattr(backend, '_item_module_lookup', None)
    if lookup and ir.message:
        unique = lookup.get("unique", {})
        missing = set()
        for m in re.finditer(r'cannot find (?:function|value|struct|type|trait) `(\w+)`', ir.message):
            missing.add(m.group(1))
        for m in re.finditer(r'undeclared type `(\w+)`', ir.message):
            missing.add(m.group(1))

        crate = (getattr(backend, '_crate_name', None) or 'crate').replace('-', '_')
        new_imports: List[str] = []
        for item in missing:
            if item in unique:
                mod = unique[item]
                use_stmt = f"use {crate}::{mod}::{item};"
                if use_stmt not in test_code:
                    new_imports.append(use_stmt)

        if new_imports:
            # Insert after the last existing use statement
            lines = test_code.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('use '):
                    insert_idx = i + 1
            for imp in new_imports:
                lines.insert(insert_idx, imp)
                insert_idx += 1
            test_code = '\n'.join(lines)
            applied.append(f"rust_add_imports({len(new_imports)})")

    return test_code, applied


def _rust_fix_type_hints(
    test_code: str, ir: DiagnosticIR, backend: Any
) -> Tuple[str, List[str]]:
    """Fix common Rust type conversion issues."""
    applied: List[str] = []

    # Fix &str vs String mismatches: suggest .to_string() or &*
    if "expected `String`, found `&str`" in ir.message or \
       "expected `&str`, found `String`" in ir.message:
        # This is too context-dependent for a blind fix
        # but we can add a helpful comment
        pass

    # Fix .into() for numeric conversions
    if "mismatched types" in ir.message and re.search(r'expected `[iu]\d+`', ir.message):
        # Can't safely auto-fix numbers, but record for memory
        pass

    return test_code, applied


def _rust_fix_visibility(
    test_code: str, ir: DiagnosticIR, backend: Any
) -> Tuple[str, List[str]]:
    """Remove or replace references to private items."""
    applied: List[str] = []

    # Detect "is private" errors and try to redirect to public API
    if "is private" in ir.message:
        # Extract the private item name
        m = re.search(r'`([^`]+)` is private', ir.message)
        if m:
            private_item = m.group(1)
            # We can't auto-fix this well — just record for memory
            pass

    return test_code, applied


# ---- Python fixers -------------------------------------------------

def _python_fix_imports(
    test_code: str, ir: DiagnosticIR, backend: Any
) -> Tuple[str, List[str]]:
    """Fix missing Python imports based on error messages."""
    applied: List[str] = []

    msg = ir.message
    # ModuleNotFoundError: No module named 'xxx'
    m = re.search(r"No module named '([^']+)'", msg)
    if m:
        module = m.group(1)
        import_line = f"import {module}"
        if import_line not in test_code:
            test_code = import_line + "\n" + test_code
            applied.append(f"python_add_import({module})")

    # ImportError: cannot import name 'X' from 'Y'
    m = re.search(r"cannot import name '([^']+)' from '([^']+)'", msg)
    if m:
        name, module = m.group(1), m.group(2)
        # Can't auto-fix (the name might not exist), but note for memory
        pass

    # NameError: name 'xxx' is not defined — possibly missing import
    m = re.search(r"name '(\w+)' is not defined", msg)
    if m:
        name = m.group(1)
        # Common patterns
        common_imports = {
            "pytest": "import pytest",
            "mock": "from unittest import mock",
            "Mock": "from unittest.mock import Mock",
            "patch": "from unittest.mock import patch",
            "MagicMock": "from unittest.mock import MagicMock",
            "os": "import os",
            "sys": "import sys",
            "json": "import json",
            "re": "import re",
            "Path": "from pathlib import Path",
            "tempfile": "import tempfile",
        }
        if name in common_imports:
            imp = common_imports[name]
            if imp not in test_code:
                test_code = imp + "\n" + test_code
                applied.append(f"python_add_common_import({name})")

    return test_code, applied


def _python_fix_syntax(
    test_code: str, ir: DiagnosticIR, backend: Any
) -> Tuple[str, List[str]]:
    """Attempt to fix trivial Python syntax errors."""
    applied: List[str] = []

    # Unclosed parenthesis at end of file
    if "unexpected EOF" in ir.message or "SyntaxError" in ir.message:
        # Count parens
        opens = test_code.count('(') - test_code.count(')')
        if opens > 0:
            test_code = test_code.rstrip() + ')' * opens + '\n'
            applied.append(f"python_close_parens({opens})")

    return test_code, applied


# ---- Go fixers -----------------------------------------------------

def _go_fix_imports(
    test_code: str, ir: DiagnosticIR, backend: Any
) -> Tuple[str, List[str]]:
    """Fix Go import issues using goimports if available."""
    applied: List[str] = []

    # "imported and not used" — remove the unused import
    for m in re.finditer(r'"([^"]+)" imported and not used', ir.message):
        pkg = m.group(1)
        # Remove the import line
        pattern = rf'^\s*"' + re.escape(pkg) + r'"\s*$'
        new_code = re.sub(pattern, '', test_code, flags=re.MULTILINE)
        if new_code != test_code:
            test_code = new_code
            applied.append(f"go_remove_unused_import({pkg})")

    # "undefined: X" — try to detect if it's from a common package
    for m in re.finditer(r'undefined: (\w+)', ir.message):
        name = m.group(1)
        # Common Go standard lib mappings
        go_imports = {
            "fmt": "fmt",
            "strings": "strings",
            "strconv": "strconv",
            "testing": "testing",
            "os": "os",
            "io": "io",
            "bytes": "bytes",
            "sort": "sort",
            "math": "math",
            "time": "time",
            "context": "context",
            "errors": "errors",
            "regexp": "regexp",
            "reflect": "reflect",
        }
        # Check if name looks like a package qualifier (e.g. "fmt" in "fmt.Println")
        if name in go_imports:
            pkg = go_imports[name]
            import_stmt = f'"{pkg}"'
            if import_stmt not in test_code:
                # Add to import block
                if 'import (' in test_code:
                    test_code = test_code.replace(
                        'import (',
                        f'import (\n\t"{pkg}"',
                        1
                    )
                else:
                    # Add import at top
                    test_code = f'import "{pkg}"\n' + test_code
                applied.append(f"go_add_import({pkg})")

    return test_code, applied


# ---- Rust cargo-check autofix --------------------------------------

def _rust_cargo_check_autofix(
    test_code: str, ir: DiagnosticIR, backend: Any
) -> Tuple[str, List[str]]:
    """Apply MachineApplicable fixes from the last cargo check diagnostic.

    This runs when the backend has already collected structured JSON
    diagnostics from ``cargo check --message-format=json``.  Those
    diagnostics include ``suggested_replacement`` fields for fixes the
    compiler is confident about (unused imports, dead code, etc.).

    The diagnostics are attached to the backend as ``_last_check_diagnostics``
    by ``measure_test_coverage`` after a failed compile step.
    """
    diagnostics = getattr(backend, '_last_check_diagnostics', None)
    if not diagnostics:
        return test_code, []

    # Only apply if the backend provides the parser method
    if not hasattr(backend, 'apply_machine_applicable_fixes'):
        return test_code, []

    patched, fix_names = backend.apply_machine_applicable_fixes(test_code, diagnostics)
    return patched, fix_names
