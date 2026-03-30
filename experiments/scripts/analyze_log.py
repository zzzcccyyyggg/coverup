#!/usr/bin/env python3
"""
CoverAgent-ML Log / Trace Analyzer
==================================
Analyzes either:
  - human-readable CoverUp log files, or
  - JSONL trace files produced by --trace-log

Usage:
    python3 experiments/scripts/analyze_log.py experiments/logs/similar_full_s42.log
    python3 experiments/scripts/analyze_log.py experiments/traces/similar_full_s42.jsonl
    python3 experiments/scripts/analyze_log.py experiments/traces/similar_full_s42.jsonl --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _base_stats() -> dict[str, Any]:
    return {
        "source_type": "",
        "attempts": 0,
        "diag_count": 0,
        "diag_categories": Counter(),
        "diag_phases": Counter(),
        "memory_injections": [],
        "memory_injection_events": 0,
        "memory_injected_attempts": 0,
        "blocker_injected_attempts": 0,
        "outcomes": Counter(),
        "repair_attempts": 0,
        "repair_successes": 0,
        "repair_partials": 0,
        "repair_fix_types": Counter(),
        "error_codes": Counter(),
        "segments_attempted": set(),
        "segments_good": set(),
        "segments_failed": set(),
        "segments_useless": set(),
        "tool_repair_attempts": 0,
        "tool_repair_success_attempts": 0,
    }


def _finalize(stats: dict[str, Any]) -> dict[str, Any]:
    stats["memory_injection_progression"] = stats["memory_injections"]
    stats["memory_max_lessons"] = max(stats["memory_injections"]) if stats["memory_injections"] else 0
    stats["memory_avg_lessons"] = (
        sum(stats["memory_injections"]) / len(stats["memory_injections"])
        if stats["memory_injections"] else 0.0
    )
    return stats


def analyze_text_log(log_path: Path) -> dict[str, Any]:
    """Parse a human-readable CoverUp log file."""
    text = log_path.read_text(errors="ignore")
    lines = text.splitlines()
    stats = _base_stats()
    stats["source_type"] = "text_log"

    for line in lines:
        # [DIAG] entries — the category might be on a continuation line
        if "[DIAG]" in line:
            stats["diag_count"] += 1

        m = re.search(r'\(category=(\w+),\s*code=([^)]*)\)', line)
        if m:
            cat = m.group(1)
            code = m.group(2).strip()
            stats["diag_categories"][cat] += 1
            if code:
                stats["error_codes"][code] += 1

        m = re.search(r'\[MEMORY\]\s*Injected\s*(\d+)\s*lessons', line)
        if m:
            stats["memory_injections"].append(int(m.group(1)))
            stats["memory_injection_events"] += 1

        if "[BLOCKER] Injected" in line:
            stats["blocker_injected_attempts"] += 1

        if "[REPAIR] Tool-first fixes applied:" in line:
            stats["repair_attempts"] += 1
            stats["tool_repair_attempts"] += 1
            fix_text = line.split("applied:", 1)[-1].strip()
            fixes = re.findall(r"'([^']+)'", fix_text)
            if not fixes and fix_text.startswith("[") and fix_text.endswith("]"):
                fixes = [s.strip().strip("'") for s in fix_text[1:-1].split(",") if s.strip()]
            for fix in fixes:
                stats["repair_fix_types"][fix] += 1

        if "[REPAIR] Tool repair succeeded" in line:
            stats["repair_successes"] += 1
            stats["tool_repair_success_attempts"] += 1

        if "[REPAIR] Tool repair partial" in line:
            stats["repair_partials"] += 1

    return _finalize(stats)


def analyze_trace(trace_path: Path) -> dict[str, Any]:
    """Parse a JSONL trace file emitted by TraceLogger."""
    stats = _base_stats()
    stats["source_type"] = "trace_jsonl"

    for raw_line in trace_path.read_text(errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        stats["attempts"] += 1

        seg_id = entry.get("seg_id")
        if seg_id:
            stats["segments_attempted"].add(seg_id)

        outcome = entry.get("outcome", "")
        if outcome:
            stats["outcomes"][outcome] += 1
            if outcome == "G" and seg_id:
                stats["segments_good"].add(seg_id)
            elif outcome == "F" and seg_id:
                stats["segments_failed"].add(seg_id)
            elif outcome == "U" and seg_id:
                stats["segments_useless"].add(seg_id)

        ir_category = entry.get("ir_category")
        if ir_category:
            stats["diag_count"] += 1
            stats["diag_categories"][ir_category] += 1

        phase = entry.get("phase")
        if phase:
            stats["diag_phases"][phase] += 1

        ir_code = entry.get("ir_code")
        if ir_code:
            stats["error_codes"][ir_code] += 1

        if entry.get("memory_injected"):
            stats["memory_injected_attempts"] += 1

        if entry.get("blocker_injected"):
            stats["blocker_injected_attempts"] += 1

        tool_fixes = entry.get("tool_fixes") or []
        if tool_fixes:
            stats["repair_attempts"] += 1
            stats["tool_repair_attempts"] += 1
            for fix in tool_fixes:
                stats["repair_fix_types"][fix] += 1
            if outcome == "G":
                stats["repair_successes"] += 1
                stats["tool_repair_success_attempts"] += 1
            elif outcome in {"F", "U", "timeout"}:
                stats["repair_partials"] += 1

    return _finalize(stats)


def analyze_path(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return analyze_trace(path)

    # Autodetect JSONL even without suffix.
    with path.open(errors="ignore") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("{") and stripped.endswith("}"):
                return analyze_trace(path)
            break

    return analyze_text_log(path)


def _to_jsonable(stats: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in stats.items():
        if isinstance(v, Counter):
            out[k] = dict(v)
        elif isinstance(v, set):
            out[k] = sorted(v)
        else:
            out[k] = v
    return out


def print_report(stats: dict[str, Any], path: Path):
    """Print a human-readable report."""
    print(f"\nCoverAgent-ML Analysis: {path.name}")
    print(f"Source type: {stats['source_type']}")
    print(f"{'='*60}")

    if stats["attempts"]:
        print(f"\n--- Attempts ---")
        print(f"  Total attempts:       {stats['attempts']}")
        print(f"  Outcomes:             {dict(stats['outcomes'])}")
        print(f"  Segments attempted:   {len(stats['segments_attempted'])}")
        print(f"  Segments good:        {len(stats['segments_good'])}")
        print(f"  Segments failed:      {len(stats['segments_failed'])}")
        print(f"  Segments useless:     {len(stats['segments_useless'])}")

    print(f"\n--- Diagnostic IR ---")
    print(f"  Total DiagIRs:        {stats['diag_count']}")
    if stats["diag_categories"]:
        print(f"  Categories:")
        for cat, count in stats["diag_categories"].most_common():
            denom = stats["diag_count"] or 1
            print(f"    {cat:<15} {count:>4} ({100*count/denom:.0f}%)")
    if stats["diag_phases"]:
        print(f"  Phases:               {dict(stats['diag_phases'])}")
    if stats["error_codes"]:
        print(f"  Top error codes:")
        for code, count in stats["error_codes"].most_common(10):
            print(f"    {code:<15} {count:>4}")

    print(f"\n--- Prompt Signals ---")
    print(f"  Memory injection events: {stats['memory_injection_events']}")
    print(f"  Memory injected attempts:{stats['memory_injected_attempts']}")
    print(f"  Blocker injected attempts:{stats['blocker_injected_attempts']}")
    if stats["memory_injections"]:
        print(f"  Max lessons injected:    {stats['memory_max_lessons']}")
        print(f"  Avg lessons injected:    {stats['memory_avg_lessons']:.1f}")
        print(
            f"  Progression: {stats['memory_injections'][:10]}"
            f"{'...' if len(stats['memory_injections']) > 10 else ''}"
        )

    print(f"\n--- Repair Orchestrator ---")
    print(f"  Tool repair attempts:    {stats['repair_attempts']}")
    print(f"  Full successes:          {stats['repair_successes']}")
    print(f"  Partial / fallback:      {stats['repair_partials']}")
    if stats["repair_fix_types"]:
        print(f"  Fix types applied:")
        for fix, count in stats["repair_fix_types"].most_common():
            print(f"    {fix:<40} {count:>4}")

    print(f"\n{'='*60}")


def main():
    ap = argparse.ArgumentParser(description="Analyze CoverAgent-ML log or trace files")
    ap.add_argument("path", type=Path, help="Path to human-readable log file or JSONL trace file")
    ap.add_argument("--json", action="store_true", help="Output as JSON")
    args = ap.parse_args()

    if not args.path.exists():
        print(f"File not found: {args.path}")
        return 1

    stats = analyze_path(args.path)

    if args.json:
        print(json.dumps(_to_jsonable(stats), indent=2))
    else:
        print_report(stats, args.path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
