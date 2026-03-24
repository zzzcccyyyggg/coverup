#!/usr/bin/env python3
"""
CoverAgent-ML Result Analyzer
==============================
Reads experiment results and generates tables for the paper.

Usage:
    python scripts/analyze_results.py                        # analyze all
    python scripts/analyze_results.py --project similar      # single project
    python scripts/analyze_results.py --latex                 # LaTeX table output
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional
import statistics


def load_results(results_dir: Path, project_filter: Optional[str] = None) -> List[dict]:
    """Load all result JSON files."""
    results = []
    for f in sorted(results_dir.glob("*.json")):
        with open(f) as fh:
            data = json.load(fh)
        if project_filter and data["project"] != project_filter:
            continue
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

    goods = [r["good"] for r in runs]
    fails = [r["failed"] for r in runs]
    useless_list = [r["useless"] for r in runs]
    line_covs = [r["line_coverage"] for r in runs]
    branch_covs = [r["branch_coverage"] for r in runs]
    costs = [r["cost_usd"] for r in runs]
    times = [r["wall_time_sec"] for r in runs]
    mem_lessons = [r.get("memory_lessons", 0) for r in runs]
    repairs = [r.get("repair_tool_fixes", 0) for r in runs]

    return {
        "n_seeds": len(runs),
        "good": mean_std(goods),
        "failed": mean_std(fails),
        "useless": mean_std(useless_list),
        "line_coverage": mean_std(line_covs),
        "branch_coverage": mean_std(branch_covs),
        "cost_usd": mean_std(costs),
        "wall_time_sec": mean_std(times),
        "memory_lessons": mean_std(mem_lessons),
        "repair_tool_fixes": mean_std(repairs),
    }


def print_ascii_table(results: List[dict]):
    """Print an ASCII comparison table."""
    groups = group_by(results, "project", "variant")

    # Get all project-variant combinations
    projects = sorted(set(r["project"] for r in results))
    variants = sorted(set(r["variant"] for r in results))

    print(f"\n{'='*100}")
    print(f"{'Project':<12} {'Variant':<12} {'Seeds':>5} "
          f"{'Good':>12} {'Failed':>12} {'Useless':>12} "
          f"{'LineCov%':>12} {'Cost$':>10} {'Time(s)':>12}")
    print(f"{'-'*100}")

    for proj in projects:
        for var in variants:
            key = (proj, var)
            if key not in groups:
                continue
            agg = compute_aggregate(groups[key])
            g_m, g_s = agg["good"]
            f_m, f_s = agg["failed"]
            u_m, u_s = agg["useless"]
            lc_m, lc_s = agg["line_coverage"]
            c_m, c_s = agg["cost_usd"]
            t_m, t_s = agg["wall_time_sec"]

            print(f"{proj:<12} {var:<12} {agg['n_seeds']:>5} "
                  f"{g_m:>5.1f}±{g_s:>4.1f} {f_m:>5.1f}±{f_s:>4.1f} {u_m:>5.1f}±{u_s:>4.1f} "
                  f"{lc_m:>5.1f}±{lc_s:>4.1f} ${c_m:>5.3f}±{c_s:>4.3f} {t_m:>5.0f}±{t_s:>4.0f}")
        print(f"{'-'*100}")

    print(f"{'='*100}")


def print_latex_table(results: List[dict]):
    """Generate LaTeX table for the paper (RQ1: main results)."""
    groups = group_by(results, "project", "variant")
    projects = sorted(set(r["project"] for r in results))

    print(r"\begin{table}[t]")
    print(r"\centering")
    print(r"\caption{Main Results: Coverage improvement across languages and projects.}")
    print(r"\label{tab:main-results}")
    print(r"\small")
    print(r"\begin{tabular}{llrrrr}")
    print(r"\toprule")
    print(r"Project & Variant & Good$\uparrow$ & Failed$\downarrow$ & LineCov\% & Cost(\$) \\")
    print(r"\midrule")

    for proj in projects:
        first = True
        for var in ["full", "no_memory", "no_repair", "no_planner", "baseline"]:
            key = (proj, var)
            if key not in groups:
                continue
            agg = compute_aggregate(groups[key])
            g_m, g_s = agg["good"]
            f_m, f_s = agg["failed"]
            lc_m, lc_s = agg["line_coverage"]
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
                  f"{fmt(lc_m, lc_s)} & {fmt(c_m, c_s)} \\\\")

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

        for var in ["no_memory", "no_repair", "no_planner", "baseline"]:
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

    results = load_results(args.results_dir, args.project)
    if not results:
        print(f"No results found in {args.results_dir}")
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
