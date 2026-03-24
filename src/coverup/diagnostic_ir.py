"""Diagnostic IR – a language-agnostic representation of verification outcomes.

Every compile / run / coverage check is normalised into a `DiagnosticIR`
instance so that the Planner, Memory and Repair modules can reason about
failures without knowing whether the project is Python, Go or Rust.

Design goals
------------
* JSON-serialisable (for logging and offline analysis).
* Compact but sufficient: captures phase, error category, cost, coverage
  delta and suggested fixes.
* Immutable once created — downstream code should *not* mutate an IR.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ── Error categories (normalised across languages) ──────────────────────

class ErrorCategory(str, Enum):
    """Normalised categories that span Python / Go / Rust."""

    IMPORT = "import"                   # missing or wrong import / use
    TYPE = "type"                       # type mismatch, wrong generic, etc.
    VISIBILITY = "visibility"           # private / unexported access
    OWNERSHIP = "ownership"             # Rust borrow / move
    SYNTAX = "syntax"                   # parse-level error
    ASSERTION = "assertion"             # test assertion failure
    PANIC = "panic"                     # runtime panic / exception
    TIMEOUT = "timeout"                 # execution timeout
    FLAKY = "flaky"                     # non-deterministic failure
    DEPENDENCY = "dependency"           # missing crate / module / package
    LINKER = "linker"                   # link-time error
    INTERFACE = "interface"             # Go interface / Rust trait mismatch
    UNKNOWN = "unknown"                 # anything that does not match above


class Phase(str, Enum):
    """Which verification stage produced this IR."""

    GENERATE = "generate"
    COMPILE = "compile"
    RUN = "run"
    COVERAGE = "coverage"
    REPAIR = "repair"
    ISOLATION = "isolation"


# ── Diagnostic IR dataclass ─────────────────────────────────────────────

@dataclass(frozen=True)
class DiagnosticIR:
    """Unified verification outcome produced by a language plugin."""

    # Identification
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    ir_version: str = "1.0"

    # Context
    language: str = ""                 # "python" | "go" | "rust"
    phase: str = Phase.COMPILE.value
    tool: str = ""                     # e.g. "cargo", "pytest", "go test"

    # Status
    status: str = "fail"               # "ok" | "fail" | "timeout"
    error_category: str = ErrorCategory.UNKNOWN.value
    error_code: str = ""               # e.g. "E0308" for Rust
    message: str = ""                  # human-readable summary (may be truncated)

    # Location (optional)
    location_file: str = ""
    location_start_line: int = 0
    location_end_line: int = 0

    # Suggested fixes from LSP / plugin rules
    suggested_fixes: Tuple[str, ...] = ()

    # Coverage delta
    coverage_before_line: float = 0.0
    coverage_before_branch: float = 0.0
    coverage_after_line: float = 0.0
    coverage_after_branch: float = 0.0
    delta_line: float = 0.0
    delta_branch: float = 0.0

    # Cost
    cost_sec: float = 0.0
    cost_tokens_in: int = 0
    cost_tokens_out: int = 0

    # Reproducibility
    seed: int = 0
    cmd: str = ""
    env_hash: str = ""

    # ── helpers ──────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert tuple to list for JSON
        d["suggested_fixes"] = list(self.suggested_fixes)
        return d

    def to_json(self, **kw) -> str:
        return json.dumps(self.to_dict(), **kw)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DiagnosticIR":
        d = dict(d)
        if "suggested_fixes" in d:
            d["suggested_fixes"] = tuple(d["suggested_fixes"])
        # Strip unknown keys (forward compat)
        known = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in known}
        return cls(**d)

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"

    @property
    def is_compile_error(self) -> bool:
        return self.phase == Phase.COMPILE.value and self.status == "fail"

    @property
    def is_runtime_error(self) -> bool:
        return self.phase == Phase.RUN.value and self.status == "fail"

    def short_summary(self) -> str:
        """One-line summary for logging / memory entries."""
        cat = self.error_category
        code = f" [{self.error_code}]" if self.error_code else ""
        msg = self.message[:120] if self.message else ""
        return f"[{self.phase}/{self.status}] {cat}{code}: {msg}"


# ── Builder helper (mutable, then freeze) ───────────────────────────────

class DiagnosticIRBuilder:
    """Convenience builder so callers don't need to pass 20+ kwargs."""

    def __init__(self, language: str = "", phase: str = Phase.COMPILE.value):
        self._kw: Dict[str, Any] = {
            "language": language,
            "phase": phase,
        }
        self._start_time: float = time.monotonic()

    # Fluent setters
    def status(self, s: str) -> "DiagnosticIRBuilder":
        self._kw["status"] = s; return self

    def ok(self) -> "DiagnosticIRBuilder":
        return self.status("ok")

    def fail(self) -> "DiagnosticIRBuilder":
        return self.status("fail")

    def timeout(self) -> "DiagnosticIRBuilder":
        return self.status("timeout")

    def error(self, category: str, code: str = "", message: str = "") -> "DiagnosticIRBuilder":
        self._kw["error_category"] = category
        if code: self._kw["error_code"] = code
        if message: self._kw["message"] = message
        return self

    def tool(self, t: str) -> "DiagnosticIRBuilder":
        self._kw["tool"] = t; return self

    def message(self, m: str) -> "DiagnosticIRBuilder":
        self._kw["message"] = m[:2000]; return self

    def location(self, file: str = "", start: int = 0, end: int = 0) -> "DiagnosticIRBuilder":
        self._kw["location_file"] = file
        self._kw["location_start_line"] = start
        self._kw["location_end_line"] = end
        return self

    def coverage_delta(self, delta_line: float = 0.0, delta_branch: float = 0.0) -> "DiagnosticIRBuilder":
        self._kw["delta_line"] = delta_line
        self._kw["delta_branch"] = delta_branch
        return self

    def suggested_fixes(self, fixes: List[str]) -> "DiagnosticIRBuilder":
        self._kw["suggested_fixes"] = tuple(fixes); return self

    def cmd(self, c: str) -> "DiagnosticIRBuilder":
        self._kw["cmd"] = c; return self

    def build(self) -> DiagnosticIR:
        elapsed = time.monotonic() - self._start_time
        self._kw.setdefault("cost_sec", round(elapsed, 3))
        return DiagnosticIR(**self._kw)


# ── Utility: classify raw error text into ErrorCategory ─────────────────

def classify_error_text(error_text: str, language: str) -> Tuple[str, str]:
    """Heuristic classifier – returns (ErrorCategory value, error_code).

    This is the *fallback*; language backends should override with more
    precise logic.
    """
    text = error_text.lower()

    if language == "rust":
        # Extract Rust error code
        import re
        m = re.search(r'error\[(E\d+)\]', error_text)
        ecode = m.group(1) if m else ""
        # Categorise by code or text
        if ecode in ("E0432", "E0433", "E0659"):
            return ErrorCategory.IMPORT.value, ecode
        if ecode in ("E0308", "E0277"):
            return ErrorCategory.TYPE.value, ecode
        if ecode in ("E0603", "E0624"):
            return ErrorCategory.VISIBILITY.value, ecode
        if ecode in ("E0505", "E0382", "E0597"):
            return ErrorCategory.OWNERSHIP.value, ecode
        if ecode in ("E0425",):
            # could be import or undeclared
            if "use" in text or "import" in text:
                return ErrorCategory.IMPORT.value, ecode
            return ErrorCategory.UNKNOWN.value, ecode
        if "panicked" in text or "thread" in text and "panicked" in text:
            return ErrorCategory.PANIC.value, ecode
        if "assertion" in text:
            return ErrorCategory.ASSERTION.value, ecode
        if ecode:
            return ErrorCategory.UNKNOWN.value, ecode

    elif language == "go":
        if "imported and not used" in text or "undefined:" in text:
            return ErrorCategory.IMPORT.value, ""
        if "cannot use" in text or "type mismatch" in text:
            return ErrorCategory.TYPE.value, ""
        if "unexported" in text or "not exported" in text:
            return ErrorCategory.VISIBILITY.value, ""
        if "does not implement" in text:
            return ErrorCategory.INTERFACE.value, ""
        if "panic:" in text:
            return ErrorCategory.PANIC.value, ""
        if "--- FAIL" in error_text:
            return ErrorCategory.ASSERTION.value, ""

    elif language == "python":
        if "importerror" in text or "modulenotfounderror" in text or "no module named" in text:
            return ErrorCategory.IMPORT.value, ""
        if "typeerror" in text:
            return ErrorCategory.TYPE.value, ""
        if "attributeerror" in text:
            return ErrorCategory.VISIBILITY.value, ""
        if "syntaxerror" in text:
            return ErrorCategory.SYNTAX.value, ""
        if "assertionerror" in text:
            return ErrorCategory.ASSERTION.value, ""
        if "timeout" in text:
            return ErrorCategory.TIMEOUT.value, ""

    # Generic fallbacks
    if "syntax" in text:
        return ErrorCategory.SYNTAX.value, ""
    if "import" in text or "module" in text:
        return ErrorCategory.IMPORT.value, ""
    if "timeout" in text:
        return ErrorCategory.TIMEOUT.value, ""
    if "panic" in text or "exception" in text:
        return ErrorCategory.PANIC.value, ""

    return ErrorCategory.UNKNOWN.value, ""
