"""Structured Trace Logger – per-attempt JSONL traces for offline analysis.

Every attempt in ``improve_coverage`` writes a single JSON line with:
  seg_id, attempt, action, ir_category, ir_code, cost_tokens, cost_sec,
  delta_line, delta_branch, outcome(G/F/U), tool_fixes, memory_injected.

This enables:
  - Statistical significance tests (paired comparisons across seeds)
  - Ablation analysis (per-module contribution)
  - Failure bottleneck analysis (which categories dominate F)
  - Token efficiency curves (coverage per 1k tokens)

The trace file is separate from the human-readable log and is always
machine-parseable (one JSON object per line).
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

from ..diagnostic_ir import DiagnosticIR


class TraceLogger:
    """Thread-safe JSONL trace writer.

    Usage::

        trace = TraceLogger("/tmp/run-trace.jsonl")
        trace.log_attempt(seg_id="src/lib.rs:42-80", attempt=1,
                          action="llm", ir=ir, outcome="F",
                          tool_fixes=[], memory_injected=True)
    """

    def __init__(self, path: Optional[str] = None):
        self._path = path
        self._lock = threading.Lock()
        self._fh = None
        self._start_time = time.monotonic()

    def _ensure_open(self):
        if self._fh is None and self._path:
            self._fh = open(self._path, "a", buffering=1)

    def log_attempt(
        self,
        seg_id: str,
        attempt: int,
        action: str,               # "llm" | "tool_repair" | "tool_repair+llm"
        ir: Optional[DiagnosticIR],
        outcome: str,              # "G" | "F" | "U" | "timeout" | "skip"
        tool_fixes: Optional[list] = None,
        memory_injected: bool = False,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Write one trace line.  No-op if path is None."""
        if not self._path:
            return

        entry = {
            "ts": round(time.monotonic() - self._start_time, 3),
            "seg_id": seg_id,
            "attempt": attempt,
            "action": action,
            "outcome": outcome,
            "memory_injected": memory_injected,
            "tool_fixes": tool_fixes or [],
        }

        if ir is not None:
            entry.update({
                "phase": ir.phase,
                "status": ir.status,
                "ir_category": ir.error_category,
                "ir_code": ir.error_code,
                "delta_line": ir.delta_line,
                "delta_branch": ir.delta_branch,
                "cost_sec": ir.cost_sec,
                "cost_tokens_in": ir.cost_tokens_in,
                "cost_tokens_out": ir.cost_tokens_out,
            })

        if extra:
            entry.update(extra)

        with self._lock:
            self._ensure_open()
            if self._fh:
                self._fh.write(json.dumps(entry, default=str) + "\n")

    def close(self) -> None:
        with self._lock:
            if self._fh:
                self._fh.close()
                self._fh = None
