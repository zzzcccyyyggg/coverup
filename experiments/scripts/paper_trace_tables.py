#!/usr/bin/env python3
"""
Paper Trace Tables
==================

Generate paper-facing markdown tables from the current targeted trace set.

This script intentionally freezes a curated slice set rather than trying to be
fully generic. Its purpose is to turn the current evidence base into reusable
paper artifacts:

1. A mechanism table showing recovery classes across representative slices.
2. A paired baseline sanity table showing where the full loop changes outcome
   class versus where slices remain prompt-first or harder-negative.

Usage:
    python3 experiments/scripts/paper_trace_tables.py --markdown
"""

from __future__ import annotations

import argparse
from pathlib import Path

from trace_matrix import summarize_trace


MECHANISM_ROWS = [
    {
        "label": "Python / click / version_option",
        "trace": "/tmp/click-full-python-seg-v18.jsonl",
        "claim_role": "repair-assisted positive",
    },
    {
        "label": "Python / click / failed variant",
        "trace": "/tmp/click-full-python-seg-v17.jsonl",
        "claim_role": "repair-engaged negative",
    },
    {
        "label": "Go / cobra / DebugFlags",
        "trace": "/tmp/cobra-debugflags-v11.jsonl",
        "claim_role": "repair-assisted positive",
    },
    {
        "label": "Go / cobra / ResetFlags",
        "trace": "/tmp/cobra-resetflags-v6.jsonl",
        "claim_role": "prompt-first positive",
    },
    {
        "label": "Go / cobra / InitDefaultHelpCmd",
        "trace": "/tmp/cobra-inithelp-v8.jsonl",
        "claim_role": "repair-engaged negative",
    },
    {
        "label": "Rust / similar / TextDiffRemapper",
        "trace": "/tmp/coverup-target-utils-noproxy.jsonl",
        "claim_role": "prompt-first positive",
    },
]

BASELINE_ROWS = [
    {
        "slice": "Python / click / version_option",
        "full_label": "full",
        "full_trace": "/tmp/click-full-python-seg-v18.jsonl",
        "baseline_label": "baseline",
        "baseline_trace": "/tmp/click-baseline-seg-v2.jsonl",
    },
    {
        "slice": "Go / cobra / DebugFlags",
        "full_label": "full",
        "full_trace": "/tmp/cobra-debugflags-v11.jsonl",
        "baseline_label": "baseline",
        "baseline_trace": "/tmp/cobra-debugflags-baseline-v1.jsonl",
    },
    {
        "slice": "Go / cobra / ResetFlags",
        "full_label": "full",
        "full_trace": "/tmp/cobra-resetflags-v6.jsonl",
        "baseline_label": "baseline",
        "baseline_trace": "/tmp/cobra-resetflags-baseline-v1.jsonl",
    },
    {
        "slice": "Go / cobra / InitDefaultHelpCmd",
        "full_label": "full",
        "full_trace": "/tmp/cobra-inithelp-v5.jsonl",
        "baseline_label": "baseline",
        "baseline_trace": "/tmp/cobra-inithelp-baseline-v1.jsonl",
    },
    {
        "slice": "Rust / similar / TextDiffRemapper",
        "full_label": "full",
        "full_trace": "/tmp/coverup-target-utils-noproxy.jsonl",
        "baseline_label": "baseline",
        "baseline_trace": "/tmp/rust-utils-baseline-v2.jsonl",
    },
]


def _load_or_stub(path_str: str) -> dict:
    path = Path(path_str)
    row = summarize_trace(path)
    row["exists"] = path.exists()
    return row


def _top_fixes(row: dict) -> str:
    fixes = row.get("tool_fixes") or []
    if not fixes:
        return "-"
    return ", ".join(fixes[:3])


def render_mechanism_markdown() -> str:
    lines = [
        "| Slice | Recovery Class | Observed Path | Last Cat | RepairEng | AvgPass | Representative Fixes | Paper Role |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for spec in MECHANISM_ROWS:
        row = _load_or_stub(spec["trace"])
        lines.append(
            "| {label} | {recovery_class} | {path} | {last_cat} | {repair} | {avg:.2f} | {fixes} | {role} |".format(
                label=spec["label"],
                recovery_class=row["recovery_class"],
                path=row["path_observed"],
                last_cat=row["last_category"],
                repair=row["repair_engaged_attempts"],
                avg=row["avg_repair_passes"],
                fixes=_top_fixes(row),
                role=spec["claim_role"],
            )
        )
    return "\n".join(lines)


def render_baseline_markdown() -> str:
    lines = [
        "| Slice | Full Path | Full Class | Baseline Path | Baseline Class | Claim Boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for spec in BASELINE_ROWS:
        full = _load_or_stub(spec["full_trace"])
        base = _load_or_stub(spec["baseline_trace"])
        if full["recovery_class"] == "repair-assisted positive" and base["recovery_class"] == "llm-only negative":
            boundary = "full-loop-dependent positive"
        elif "positive" in full["recovery_class"] and "positive" in base["recovery_class"]:
            boundary = "prompt-first or easier positive"
        elif "negative" in full["recovery_class"] and "negative" in base["recovery_class"]:
            boundary = "harder negative paired contrast"
        else:
            boundary = "mixed paired contrast"
        lines.append(
            "| {slice} | {full_path} | {full_class} | {base_path} | {base_class} | {boundary} |".format(
                slice=spec["slice"],
                full_path=full["path_observed"],
                full_class=full["recovery_class"],
                base_path=base["path_observed"],
                base_class=base["recovery_class"],
                boundary=boundary,
            )
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate paper-facing trace tables.")
    ap.add_argument("--markdown", action="store_true", help="Emit markdown tables")
    args = ap.parse_args()

    if args.markdown:
        print("## Mechanism Table")
        print()
        print(render_mechanism_markdown())
        print()
        print("## Paired Baseline Table")
        print()
        print(render_baseline_markdown())
        return 0

    print(render_mechanism_markdown())
    print()
    print(render_baseline_markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
