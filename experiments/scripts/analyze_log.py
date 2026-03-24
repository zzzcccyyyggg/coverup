#!/usr/bin/env python3
"""
CoverAgent-ML Log Analyzer
===========================
Analyzes CoverUp log files to extract DiagnosticIR statistics,
repair effectiveness, and memory utilization.

Usage:
    python scripts/analyze_log.py /tmp/similar-agent-log
    python scripts/analyze_log.py /tmp/similar-agent-log --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def analyze_log(log_path: Path) -> dict:
    """Parse a CoverUp log file and extract agent statistics."""
    text = log_path.read_text(errors="ignore")
    lines = text.split("\n")

    stats = {
        "diag_count": 0,
        "diag_categories": Counter(),
        "diag_phases": Counter(),
        "memory_injections": [],
        "repair_attempts": 0,
        "repair_successes": 0,
        "repair_partials": 0,
        "repair_fix_types": Counter(),
        "agent_tool_repairs_per_segment": Counter(),
        "error_codes": Counter(),
        "segments_attempted": set(),
        "segments_good": set(),
        "segments_failed": set(),
        "segments_useless": set(),
    }

    for line in lines:
        # [DIAG] entries — the category might be on a continuation line
        if "[DIAG]" in line:
            stats["diag_count"] += 1

        # Category extraction: look for (category=X, code=Y) anywhere
        m = re.search(r'\(category=(\w+),\s*code=([^)]*)\)', line)
        if m:
            cat = m.group(1)
            code = m.group(2).strip()
            stats["diag_categories"][cat] += 1
            if code:
                stats["error_codes"][code] += 1

        # [MEMORY] injections
        m = re.search(r'\[MEMORY\]\s*Injected\s*(\d+)\s*lessons', line)
        if m:
            stats["memory_injections"].append(int(m.group(1)))

        # [REPAIR] entries
        if "[REPAIR] Tool-first fixes applied:" in line:
            stats["repair_attempts"] += 1
            m = re.search(r"\[([^\]]+)\]$", line)
            if m:
                fixes = m.group(1).replace("'", "").split(", ")
                for fix in fixes:
                    stats["repair_fix_types"][fix.strip()] += 1

        if "[REPAIR] Tool repair succeeded" in line:
            stats["repair_successes"] += 1

        if "[REPAIR] Tool repair partial" in line:
            stats["repair_partials"] += 1

        # Segment outcomes
        m = re.search(r'Saved as (.+)', line)
        if m:
            # This is a successful save
            pass

    # Compute summary
    stats["memory_injection_progression"] = stats["memory_injections"]
    stats["memory_max_lessons"] = max(stats["memory_injections"]) if stats["memory_injections"] else 0
    stats["memory_avg_lessons"] = (
        sum(stats["memory_injections"]) / len(stats["memory_injections"])
        if stats["memory_injections"] else 0
    )

    return stats


def print_report(stats: dict, log_path: Path):
    """Print a human-readable report."""
    print(f"\nCoverAgent-ML Log Analysis: {log_path.name}")
    print(f"{'='*60}")

    print(f"\n--- Diagnostic IR ---")
    print(f"  Total DiagIRs:  {stats['diag_count']}")
    print(f"  Categories:")
    for cat, count in stats["diag_categories"].most_common():
        print(f"    {cat:<15} {count:>4} ({100*count/stats['diag_count']:.0f}%)")
    if stats["error_codes"]:
        print(f"  Top error codes:")
        for code, count in stats["error_codes"].most_common(10):
            print(f"    {code:<15} {count:>4}")

    print(f"\n--- Reflective Memory ---")
    print(f"  Injection events:     {len(stats['memory_injections'])}")
    print(f"  Max lessons injected: {stats['memory_max_lessons']}")
    print(f"  Avg lessons injected: {stats['memory_avg_lessons']:.1f}")
    if stats["memory_injections"]:
        print(f"  Progression: {stats['memory_injections'][:10]}{'...' if len(stats['memory_injections'])>10 else ''}")

    print(f"\n--- Repair Orchestrator ---")
    print(f"  Tool repair attempts:  {stats['repair_attempts']}")
    print(f"  Full successes:        {stats['repair_successes']}")
    print(f"  Partial (LLM fallback):{stats['repair_partials']}")
    if stats["repair_fix_types"]:
        print(f"  Fix types applied:")
        for fix, count in stats["repair_fix_types"].most_common():
            print(f"    {fix:<40} {count:>4}")

    print(f"\n{'='*60}")


def main():
    ap = argparse.ArgumentParser(description="Analyze CoverAgent-ML log files")
    ap.add_argument("log_file", type=Path, help="Path to log file")
    ap.add_argument("--json", action="store_true", help="Output as JSON")
    args = ap.parse_args()

    if not args.log_file.exists():
        print(f"Log file not found: {args.log_file}")
        return 1

    stats = analyze_log(args.log_file)

    if args.json:
        # Convert Counter/set to serializable types
        out = {}
        for k, v in stats.items():
            if isinstance(v, Counter):
                out[k] = dict(v)
            elif isinstance(v, set):
                out[k] = sorted(v)
            else:
                out[k] = v
        print(json.dumps(out, indent=2))
    else:
        print_report(stats, args.log_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
