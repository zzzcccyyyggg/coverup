#!/usr/bin/env python3
"""
Trace Matrix Builder
====================

Build a compact, paper-friendly matrix from one or more JSONL trace files.

Unlike analyze_results.py, this script is intended for targeted slice traces,
including partial / interrupted runs. Therefore it reports *observed* paths
rather than assuming every trace reached a complete terminal evaluation.

Usage:
    python3 experiments/scripts/trace_matrix.py /tmp/click-full-python-seg-v18.jsonl
    python3 experiments/scripts/trace_matrix.py /tmp/*.jsonl --markdown
    python3 experiments/scripts/trace_matrix.py /tmp/*.jsonl --json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_trace(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for raw_line in path.read_text(errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        entries.append(entry)
    return entries


def _compress_runs(values: list[str]) -> str:
    if not values:
        return "-"
    out: list[str] = []
    prev = values[0]
    count = 1
    for value in values[1:]:
        if value == prev:
            count += 1
            continue
        out.append(f"{prev} x{count}" if count > 1 else prev)
        prev = value
        count = 1
    out.append(f"{prev} x{count}" if count > 1 else prev)
    return " -> ".join(out)


def _short_path(entries: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for entry in entries:
        action = entry.get("action") or "?"
        outcome = entry.get("outcome") or "?"
        parts.append(f"{action}/{outcome}")
    return _compress_runs(parts)


def summarize_trace(path: Path) -> dict[str, Any]:
    entries = load_trace(path)
    if not entries:
        return {
            "label": path.stem,
            "trace": str(path),
            "attempts_observed": 0,
            "segment": "-",
            "path_observed": "-",
            "actions_observed": "-",
            "outcomes_observed": "-",
            "last_outcome": "-",
            "last_category": "-",
            "repair_engaged_attempts": 0,
            "avg_repair_passes": 0.0,
            "max_repair_passes": 0,
            "fixpoint_exhausted": 0,
            "tool_fixes": [],
        }

    seg_id = entries[0].get("seg_id", "")
    segment = Path(seg_id).name if seg_id else "-"

    actions = [str(entry.get("action") or "?") for entry in entries]
    outcomes = [str(entry.get("outcome") or "?") for entry in entries]
    categories = [str(entry.get("ir_category") or "?") for entry in entries]
    repair_passes = [int(entry.get("repair_passes", 0) or 0) for entry in entries]
    fixpoint_exhausted = sum(1 for entry in entries if entry.get("fixpoint_exhausted"))
    repair_engaged_attempts = sum(
        1
        for entry in entries
        if entry.get("tool_fixes") or str(entry.get("action", "")).startswith("tool_repair")
    )

    fix_counter: Counter[str] = Counter()
    for entry in entries:
        for fix in entry.get("tool_fixes") or []:
            fix_counter[str(fix)] += 1

    saw_good = any(outcome == "G" for outcome in outcomes)
    if saw_good and repair_engaged_attempts > 0:
        recovery_class = "repair-assisted positive"
    elif saw_good:
        recovery_class = "prompt-first positive"
    elif repair_engaged_attempts > 0:
        recovery_class = "repair-engaged negative"
    else:
        recovery_class = "llm-only negative"

    return {
        "label": path.stem,
        "trace": str(path),
        "attempts_observed": len(entries),
        "segment": segment,
        "path_observed": _short_path(entries),
        "actions_observed": _compress_runs(actions),
        "outcomes_observed": _compress_runs(outcomes),
        "last_outcome": outcomes[-1],
        "last_category": categories[-1],
        "repair_engaged_attempts": repair_engaged_attempts,
        "avg_repair_passes": (sum(repair_passes) / len(repair_passes)) if repair_passes else 0.0,
        "max_repair_passes": max(repair_passes) if repair_passes else 0,
        "fixpoint_exhausted": fixpoint_exhausted,
        "tool_fixes": [fix for fix, _ in fix_counter.most_common(8)],
        "recovery_class": recovery_class,
    }


def print_markdown(rows: list[dict[str, Any]]) -> None:
    print("| Label | Segment | Attempts | Recovery Class | Observed Path | Last Cat | RepairEng | AvgPass | FixExh | Top Fixes |")
    print("| --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: | --- |")
    for row in rows:
        fixes = ", ".join(row["tool_fixes"]) if row["tool_fixes"] else "-"
        print(
            f"| {row['label']} | {row['segment']} | {row['attempts_observed']} | "
            f"{row['recovery_class']} | {row['path_observed']} | {row['last_category']} | "
            f"{row['repair_engaged_attempts']} | {row['avg_repair_passes']:.2f} | "
            f"{row['fixpoint_exhausted']} | {fixes} |"
        )


def print_text(rows: list[dict[str, Any]]) -> None:
    print(
        f"{'Label':<32} {'Attempts':>8} {'Last':>6} {'LastCat':>12} "
        f"{'RepairEng':>10} {'AvgPass':>8} {'FixExh':>8}  Path"
    )
    print("-" * 140)
    for row in rows:
        print(
            f"{row['label']:<32} {row['attempts_observed']:>8} {row['last_outcome']:>6} "
            f"{row['last_category']:>12} {row['repair_engaged_attempts']:>10} "
            f"{row['avg_repair_passes']:>8.2f} {row['fixpoint_exhausted']:>8}  "
            f"{row['path_observed']}"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a compact matrix from targeted JSONL traces.")
    ap.add_argument("traces", nargs="+", help="Trace JSONL files to summarize")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output")
    ap.add_argument("--markdown", action="store_true", help="Emit a markdown table")
    args = ap.parse_args()

    rows = [summarize_trace(Path(trace)) for trace in args.traces]

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    if args.markdown:
        print_markdown(rows)
        return 0

    print_text(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
