#!/usr/bin/env python3
"""
CoverAgent-ML Result Analyzer
==============================
Reads experiment results and generates tables for the paper.

Usage:
    python3 experiments/scripts/analyze_results.py
    python3 experiments/scripts/analyze_results.py --project similar
    python3 experiments/scripts/analyze_results.py --latex
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional
import statistics


VARIANT_ORDER = ["full", "no_memory", "no_repair", "no_planner", "no_blocker", "baseline"]
REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve_optional_path(path_str: str) -> Optional[Path]:
    """Resolve an optional path string from a result JSON."""
    if not path_str:
        return None
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def derive_trace_metrics(trace_path: Path) -> dict:
    """Derive terminal attempt metrics from a JSONL trace file."""
    terminal_good = 0
    terminal_failed = 0
    terminal_useless = 0
    trace_attempts = 0
    repair_attempts = 0
    repair_passes: List[int] = []
    fixpoint_exhausted_attempts = 0

    for raw_line in trace_path.read_text(errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        trace_attempts += 1
        outcome = entry.get("outcome")
        if outcome == "G":
            terminal_good += 1
        elif outcome == "F":
            terminal_failed += 1
        elif outcome == "U":
            terminal_useless += 1

        if entry.get("tool_fixes"):
            repair_attempts += 1

        repair_passes.append(int(entry.get("repair_passes", 0) or 0))
        if entry.get("fixpoint_exhausted"):
            fixpoint_exhausted_attempts += 1

    avg_repair_passes = statistics.mean(repair_passes) if repair_passes else 0.0
    max_repair_passes = max(repair_passes) if repair_passes else 0

    return {
        "terminal_good": terminal_good,
        "terminal_failed": terminal_failed,
        "terminal_useless": terminal_useless,
        "trace_attempts": trace_attempts,
        "repair_attempts_terminal": repair_attempts,
        "avg_repair_passes": avg_repair_passes,
        "max_repair_passes_seen": max_repair_passes,
        "fixpoint_exhausted_attempts": fixpoint_exhausted_attempts,
        "trace_available": True,
    }


def load_results(results_dir: Path, project_filter: Optional[str] = None) -> List[dict]:
    """Load all result JSON files."""
    results = []
    for f in sorted(results_dir.glob("*.json")):
        with open(f) as fh:
            data = json.load(fh)
        if project_filter and data["project"] != project_filter:
            continue
        trace_path = resolve_optional_path(data.get("trace_file", ""))
        if trace_path and trace_path.exists():
            data.update(derive_trace_metrics(trace_path))
        else:
            data.update({
                "terminal_good": data.get("good", 0),
                "terminal_failed": data.get("failed", 0),
                "terminal_useless": data.get("useless", 0),
                "trace_attempts": data.get("good", 0) + data.get("failed", 0) + data.get("useless", 0),
                "repair_attempts_terminal": 0,
                "avg_repair_passes": 0.0,
                "max_repair_passes_seen": 0,
                "fixpoint_exhausted_attempts": 0,
                "trace_available": False,
            })
        data["raw_failed"] = data.get("failed", 0)
        results.append(data)
    return results


def group_by(results: List[dict], *keys) -> Dict[tuple, List[dict]]:
    """Group results by specified keys."""
    groups = defaultdict(list)
    for r in results:
        key = tuple(r[k] for k in keys)
        groups[key].append(r)
    return groups


def mean_std(values: List[float]) -> tuple:
    """Return (mean, std) for a list of values."""
    if not values:
        return (0.0, 0.0)
    m = statistics.mean(values)
    s = statistics.stdev(values) if len(values) > 1 else 0.0
    return (m, s)


def compute_aggregate(runs: List[dict]) -> dict:
    """Compute aggregate metrics over multiple seeds."""
    if not runs:
        return {}

    goods = [r.get("terminal_good", r["good"]) for r in runs]
    fails = [r.get("terminal_failed", r["failed"]) for r in runs]
    useless_list = [r.get("terminal_useless", r["useless"]) for r in runs]
    raw_failed = [r.get("raw_failed", r["failed"]) for r in runs]
    init_covs = [r.get("initial_line_coverage", 0.0) for r in runs]
    line_covs = [r["line_coverage"] for r in runs]
    cov_deltas = [r.get("coverage_delta", r["line_coverage"] - r.get("initial_line_coverage", 0.0)) for r in runs]
    branch_covs = [r["branch_coverage"] for r in runs]
    costs = [r["cost_usd"] for r in runs]
    times = [r["wall_time_sec"] for r in runs]
    mem_lessons = [r.get("memory_lessons", 0) for r in runs]
    repairs = [r.get("repair_tool_fixes", 0) for r in runs]
    trace_attempts = [r.get("trace_attempts", 0) for r in runs]
    repair_pass_means = [r.get("avg_repair_passes", 0.0) for r in runs]
    fixpoint_exhausted = [r.get("fixpoint_exhausted_attempts", 0) for r in runs]
    trace_runs = sum(1 for r in runs if r.get("trace_available"))
    error_runs = sum(1 for r in runs if r.get("error"))

    return {
        "n_seeds": len(runs),
        "good": mean_std(goods),
        "failed": mean_std(fails),
        "raw_failed": mean_std(raw_failed),
        "useless": mean_std(useless_list),
        "initial_line_coverage": mean_std(init_covs),
        "line_coverage": mean_std(line_covs),
        "coverage_delta": mean_std(cov_deltas),
        "branch_coverage": mean_std(branch_covs),
        "cost_usd": mean_std(costs),
        "wall_time_sec": mean_std(times),
        "memory_lessons": mean_std(mem_lessons),
        "repair_tool_fixes": mean_std(repairs),
        "trace_attempts": mean_std(trace_attempts),
        "avg_repair_passes": mean_std(repair_pass_means),
        "fixpoint_exhausted_attempts": mean_std(fixpoint_exhausted),
        "trace_runs": trace_runs,
        "error_runs": error_runs,
    }


def print_ascii_table(results: List[dict]):
    """Print an ASCII comparison table."""
    groups = group_by(results, "project", "variant")

    # Get all project-variant combinations
    projects = sorted(set(r["project"] for r in results))
    variants = [v for v in VARIANT_ORDER if v in {r["variant"] for r in results}]

    print("\n[Analyzer] Good/Failed/Useless are terminal attempt outcomes from trace when available.")
    print("[Analyzer] RawF counts internal compile/run failure events from the summary JSON.")
    print(f"\n{'='*145}")
    print(f"{'Project':<12} {'Variant':<12} {'Seeds':>5} "
          f"{'Good':>12} {'Failed':>12} {'RawF':>12} {'Useless':>12} "
          f"{'FinalCov%':>12} {'Delta(pp)':>12} {'AvgPass':>10} {'FixExh':>10} {'ErrRuns':>8}")
    print(f"{'-'*145}")

    for proj in projects:
        for var in variants:
            key = (proj, var)
            if key not in groups:
                continue
            agg = compute_aggregate(groups[key])
            g_m, g_s = agg["good"]
            f_m, f_s = agg["failed"]
            rf_m, rf_s = agg["raw_failed"]
            u_m, u_s = agg["useless"]
            lc_m, lc_s = agg["line_coverage"]
            dc_m, dc_s = agg["coverage_delta"]
            rp_m, rp_s = agg["avg_repair_passes"]
            fx_m, fx_s = agg["fixpoint_exhausted_attempts"]
            err_runs = agg["error_runs"]

            print(f"{proj:<12} {var:<12} {agg['n_seeds']:>5} "
                  f"{g_m:>5.1f}±{g_s:>4.1f} {f_m:>5.1f}±{f_s:>4.1f} {rf_m:>5.1f}±{rf_s:>4.1f} {u_m:>5.1f}±{u_s:>4.1f} "
                  f"{lc_m:>5.1f}±{lc_s:>4.1f} {dc_m:>+5.1f}±{dc_s:>4.1f} {rp_m:>5.2f}±{rp_s:>4.2f} {fx_m:>5.1f}±{fx_s:>4.1f} {err_runs:>8}")
        print(f"{'-'*145}")

    print(f"{'='*145}")


def print_latex_table(results: List[dict]):
    """Generate LaTeX table for the paper (RQ1: main results)."""
    groups = group_by(results, "project", "variant")
    projects = sorted(set(r["project"] for r in results))

    print(r"\begin{table}[t]")
    print(r"\centering")
    print(r"\caption{Main Results: Coverage improvement across languages and projects.}")
    print(r"\label{tab:main-results}")
    print(r"\small")
    print(r"\begin{tabular}{llrrrrr}")
    print(r"\toprule")
    print(r"Project & Variant & Good$\uparrow$ & Failed$\downarrow$ & FinalCov\% & $\Delta$Cov & Cost(\$) \\")
    print(r"\midrule")

    for proj in projects:
        first = True
        for var in VARIANT_ORDER:
            key = (proj, var)
            if key not in groups:
                continue
            agg = compute_aggregate(groups[key])
            g_m, g_s = agg["good"]
            f_m, f_s = agg["failed"]
            lc_m, lc_s = agg["line_coverage"]
            dc_m, dc_s = agg["coverage_delta"]
            c_m, c_s = agg["cost_usd"]

            proj_col = proj if first else ""
            first = False
            var_label = var.replace("_", r"\_")

            # Bold the best (full) variant
            bold = var == "full"
            fmt = lambda v, s: (f"\\textbf{{{v:.1f}}}$\\pm${s:.1f}" if bold
                               else f"{v:.1f}$\\pm${s:.1f}")

            print(f"  {proj_col} & {var_label} & "
                  f"{fmt(g_m, g_s)} & {fmt(f_m, f_s)} & "
                  f"{fmt(lc_m, lc_s)} & {fmt(dc_m, dc_s)} & {fmt(c_m, c_s)} \\\\")

        print(r"\midrule")

    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")


def print_ablation_delta(results: List[dict]):
    """Print ablation deltas (difference from full variant)."""
    groups = group_by(results, "project", "variant")
    projects = sorted(set(r["project"] for r in results))

    print(f"\n{'='*80}")
    print(f"ABLATION DELTAS (Full - Variant)")
    print(f"{'='*80}")
    print(f"{'Project':<12} {'Variant':<12} {'ΔGood':>8} {'ΔFailed':>8} {'ΔLineCov':>10} {'ΔCost':>8}")
    print(f"{'-'*80}")

    for proj in projects:
        full_key = (proj, "full")
        if full_key not in groups:
            continue
        full_agg = compute_aggregate(groups[full_key])

        for var in [v for v in VARIANT_ORDER if v not in {"full"}]:
            key = (proj, var)
            if key not in groups:
                continue
            agg = compute_aggregate(groups[key])

            dg = full_agg["good"][0] - agg["good"][0]
            df = full_agg["failed"][0] - agg["failed"][0]
            dlc = full_agg["line_coverage"][0] - agg["line_coverage"][0]
            dc = full_agg["cost_usd"][0] - agg["cost_usd"][0]

            print(f"{proj:<12} {var:<12} {dg:>+7.1f} {df:>+7.1f} {dlc:>+9.1f}% ${dc:>+6.3f}")
        print()

    print(f"{'='*80}")


def main():
    ap = argparse.ArgumentParser(description="CoverAgent-ML Result Analyzer")
    ap.add_argument("--results-dir", type=Path, default=Path("experiments/results"),
                    help="Directory with result JSON files")
    ap.add_argument("--project", type=str, help="Filter to specific project")
    ap.add_argument("--latex", action="store_true", help="Output LaTeX table")
    ap.add_argument("--ablation", action="store_true", help="Show ablation deltas")
    args = ap.parse_args()

    results_dir = args.results_dir if args.results_dir.is_absolute() else (REPO_ROOT / args.results_dir)
    results = load_results(results_dir, args.project)
    if not results:
        print(f"No results found in {results_dir}")
        return 1

    print(f"Loaded {len(results)} result files")

    if args.latex:
        print_latex_table(results)
    elif args.ablation:
        print_ablation_delta(results)
    else:
        print_ascii_table(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
