#!/usr/bin/env python3
"""
CoverAgent-ML Experiment Runner
================================
Runs the full experiment matrix: projects × seeds × ablation variants.
Collects results into CSV for analysis.

Usage:
    python scripts/run_experiments.py                           # full run
    python scripts/run_experiments.py --project similar         # single project
    python scripts/run_experiments.py --variant full baseline   # specific variants
    python scripts/run_experiments.py --seed 42                 # single seed
    python scripts/run_experiments.py --dry-run                 # plan only
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Data classes ────────────────────────────────────────────────────────

@dataclass
class ProjectConfig:
    name: str
    language: str
    repo: str
    tag: str
    source_dir: str
    prompt: str
    notes: str = ""


@dataclass
class RunResult:
    project: str
    language: str
    variant: str
    seed: int
    good: int = 0
    failed: int = 0
    useless: int = 0
    total_segments: int = 0
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    cost_usd: float = 0.0
    wall_time_sec: float = 0.0
    memory_lessons: int = 0
    repair_tool_fixes: int = 0
    planner_pulls: int = 0
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "project": self.project,
            "language": self.language,
            "variant": self.variant,
            "seed": self.seed,
            "good": self.good,
            "failed": self.failed,
            "useless": self.useless,
            "total_segments": self.total_segments,
            "line_coverage": self.line_coverage,
            "branch_coverage": self.branch_coverage,
            "cost_usd": self.cost_usd,
            "wall_time_sec": self.wall_time_sec,
            "memory_lessons": self.memory_lessons,
            "repair_tool_fixes": self.repair_tool_fixes,
            "planner_pulls": self.planner_pulls,
            "error": self.error,
        }


# ── Helpers ─────────────────────────────────────────────────────────────

def load_config(path: str = "scripts/experiment_config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def ensure_project(proj: ProjectConfig, workspace: Path) -> Path:
    """Clone and checkout the project if needed. Returns project dir."""
    proj_dir = workspace / proj.name
    if proj_dir.exists():
        print(f"  [skip] {proj.name} already cloned at {proj_dir}")
        return proj_dir

    print(f"  [clone] {proj.name} from {proj.repo} @ {proj.tag}")
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", proj.tag, proj.repo, str(proj_dir)],
        check=True, capture_output=True, text=True,
    )
    return proj_dir


def clean_generated_tests(proj_dir: Path, language: str):
    """Remove previously generated test files."""
    if language == "rust":
        tests_dir = proj_dir / "tests"
        if tests_dir.exists():
            for f in tests_dir.glob("coverup_*.rs"):
                f.unlink()
    elif language == "python":
        tests_dir = proj_dir / "tests"
        if tests_dir.exists():
            for f in tests_dir.glob("test_coverup_*.py"):
                f.unlink()
    elif language == "go":
        for f in proj_dir.rglob("coverup_*_test.go"):
            f.unlink()


def build_coverup_cmd(
    proj: ProjectConfig,
    proj_dir: Path,
    variant_flags: List[str],
    seed: int,
    config: dict,
    log_file: Path,
) -> List[str]:
    """Build the CoverUp command for a single run."""
    llm_cfg = config["llm"]

    cmd = [
        sys.executable, "-m", "coverup",
        "--language", proj.language,
        "--source-dir", str(proj_dir / proj.source_dir),
        "--prompt", proj.prompt,
        "--model", llm_cfg["model"],
        "--model-temperature", str(llm_cfg["temperature"]),
        "--max-concurrency", str(llm_cfg["max_concurrency"]),
        "--max-attempts", str(llm_cfg["max_attempts"]),
        "--log-file", str(log_file),
    ]

    # Tests dir
    if proj.language == "rust":
        tests_dir = proj_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        cmd.extend(["--tests-dir", str(tests_dir)])
    elif proj.language == "python":
        tests_dir = proj_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        cmd.extend(["--tests-dir", str(tests_dir)])

    # Variant-specific flags
    cmd.extend(variant_flags)

    return cmd


def parse_output(output: str, log_file: Path) -> Dict[str, Any]:
    """Parse the CoverUp output to extract metrics."""
    result = {}

    # Parse final progress bar line: G=XX, F=XX, U=XX
    m = re.search(r'G=(\d+),\s*F=(\d+),\s*U=(\d+)', output)
    if m:
        result["good"] = int(m.group(1))
        result["failed"] = int(m.group(2))
        result["useless"] = int(m.group(3))

    # Parse total segments from progress bar: XX/YY
    m = re.search(r'(\d+)/(\d+)\s*\[', output)
    if m:
        result["total_segments"] = int(m.group(2))

    # Parse cost
    m = re.search(r'cost=~\$([0-9.]+)', output)
    if m:
        result["cost_usd"] = float(m.group(1))

    # Parse coverage from final measurement
    m = re.search(r'line\s+coverage[:\s]+([0-9.]+)%', output, re.IGNORECASE)
    if m:
        result["line_coverage"] = float(m.group(1))

    m = re.search(r'branch\s+coverage[:\s]+([0-9.]+)%', output, re.IGNORECASE)
    if m:
        result["branch_coverage"] = float(m.group(1))

    # Parse agent stats from [CoverAgent-ML] output
    m = re.search(r'Memory:\s*(\d+)\s*lessons', output)
    if m:
        result["memory_lessons"] = int(m.group(1))

    m = re.search(r'Planner:\s*(\d+)\s*pulls', output)
    if m:
        result["planner_pulls"] = int(m.group(1))

    # Count tool-first repairs from log
    if log_file.exists():
        log_text = log_file.read_text(errors="ignore")
        result["repair_tool_fixes"] = log_text.count("[REPAIR] Tool-first fixes applied")

    return result


# ── Main runner ─────────────────────────────────────────────────────────

def run_single(
    proj: ProjectConfig,
    variant_name: str,
    variant_flags: List[str],
    seed: int,
    config: dict,
    workspace: Path,
    results_dir: Path,
    logs_dir: Path,
) -> RunResult:
    """Run CoverUp once and collect results."""
    run_id = f"{proj.name}_{variant_name}_s{seed}"
    print(f"\n{'='*60}")
    print(f"  RUN: {run_id}")
    print(f"  Project: {proj.name} ({proj.language})")
    print(f"  Variant: {variant_name}")
    print(f"  Seed: {seed}")
    print(f"{'='*60}")

    result = RunResult(
        project=proj.name,
        language=proj.language,
        variant=variant_name,
        seed=seed,
    )

    proj_dir = ensure_project(proj, workspace)

    # Clean old generated tests
    clean_generated_tests(proj_dir, proj.language)

    # Log file for this run
    log_file = logs_dir / f"{run_id}.log"

    # Build command
    cmd = build_coverup_cmd(proj, proj_dir, variant_flags, seed, config, log_file)

    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "src")

    # API key
    api_key_env = config["llm"].get("api_key_env", "DEEPSEEK_API_KEY")
    if api_key_env in os.environ:
        env[api_key_env] = os.environ[api_key_env]

    print(f"  CMD: {' '.join(cmd[:8])}...")

    # Run with timeout
    timeout = config.get("timeouts", {}).get("per_project_seconds", 3600)
    t0 = time.time()

    try:
        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(proj_dir) if proj.language in ("go",) else None,
        )
        wall_time = time.time() - t0
        output = proc.stdout + proc.stderr

        # Parse metrics from output
        metrics = parse_output(output, log_file)
        result.good = metrics.get("good", 0)
        result.failed = metrics.get("failed", 0)
        result.useless = metrics.get("useless", 0)
        result.total_segments = metrics.get("total_segments", 0)
        result.line_coverage = metrics.get("line_coverage", 0.0)
        result.branch_coverage = metrics.get("branch_coverage", 0.0)
        result.cost_usd = metrics.get("cost_usd", 0.0)
        result.wall_time_sec = wall_time
        result.memory_lessons = metrics.get("memory_lessons", 0)
        result.repair_tool_fixes = metrics.get("repair_tool_fixes", 0)
        result.planner_pulls = metrics.get("planner_pulls", 0)

        if proc.returncode != 0:
            result.error = f"exit_code={proc.returncode}"

    except subprocess.TimeoutExpired:
        wall_time = time.time() - t0
        result.wall_time_sec = wall_time
        result.error = "timeout"
        print(f"  [TIMEOUT] after {wall_time:.0f}s")

    except Exception as e:
        wall_time = time.time() - t0
        result.wall_time_sec = wall_time
        result.error = str(e)[:200]
        print(f"  [ERROR] {e}")

    # Save individual result JSON
    result_file = results_dir / f"{run_id}.json"
    with open(result_file, "w") as f:
        json.dump(result.to_dict(), f, indent=2)

    print(f"  Result: G={result.good}, F={result.failed}, U={result.useless}")
    print(f"  Coverage: line={result.line_coverage:.1f}%, branch={result.branch_coverage:.1f}%")
    print(f"  Cost: ${result.cost_usd:.3f}, Time: {result.wall_time_sec:.0f}s")
    if result.error:
        print(f"  Error: {result.error}")

    return result


def write_summary_csv(results: List[RunResult], path: Path):
    """Write all results to a CSV summary file."""
    if not results:
        return

    fieldnames = list(results[0].to_dict().keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r.to_dict())

    print(f"\nSummary written to {path}")


def print_summary_table(results: List[RunResult]):
    """Print a compact ASCII table of results."""
    if not results:
        return

    print(f"\n{'='*90}")
    print(f"{'Project':<12} {'Variant':<12} {'Seed':>4} {'G':>4} {'F':>4} {'U':>4} "
          f"{'Line%':>7} {'Br%':>7} {'Cost':>7} {'Time':>6} {'Mem':>4} {'Rep':>4}")
    print(f"{'-'*90}")

    for r in sorted(results, key=lambda x: (x.project, x.variant, x.seed)):
        print(f"{r.project:<12} {r.variant:<12} {r.seed:>4} {r.good:>4} {r.failed:>4} {r.useless:>4} "
              f"{r.line_coverage:>6.1f}% {r.branch_coverage:>6.1f}% "
              f"${r.cost_usd:>5.3f} {r.wall_time_sec:>5.0f}s {r.memory_lessons:>4} {r.repair_tool_fixes:>4}")

    print(f"{'='*90}")


def main():
    ap = argparse.ArgumentParser(
        description="CoverAgent-ML Experiment Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("--config", default="scripts/experiment_config.yaml",
                    help="Path to experiment config YAML")
    ap.add_argument("--project", nargs="*", help="Run only these projects")
    ap.add_argument("--variant", nargs="*", help="Run only these variants")
    ap.add_argument("--seed", type=int, nargs="*", help="Run only these seeds")
    ap.add_argument("--workspace", type=Path, default=Path("/tmp/coveragent-experiments"),
                    help="Directory to clone projects into")
    ap.add_argument("--dry-run", action="store_true", help="Print plan without executing")
    ap.add_argument("--resume", action="store_true",
                    help="Skip runs that already have result JSONs")
    args = ap.parse_args()

    # Load config
    config = load_config(args.config)

    # Parse projects
    projects = []
    for p in config["projects"]:
        proj = ProjectConfig(**{k: v for k, v in p.items() if k in ProjectConfig.__dataclass_fields__})
        if args.project and proj.name not in args.project:
            continue
        projects.append(proj)

    # Parse variants
    variants = config.get("variants", {})
    if args.variant:
        variants = {k: v for k, v in variants.items() if k in args.variant}

    # Parse seeds
    seeds = args.seed or config.get("seeds", [42])

    # Output dirs
    results_dir = Path(config["output"]["results_dir"])
    logs_dir = Path(config["output"]["logs_dir"])
    summary_file = Path(config["output"]["summary_file"])

    results_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    args.workspace.mkdir(parents=True, exist_ok=True)

    # Build run matrix
    runs = []
    for proj in projects:
        for vname, vcfg in variants.items():
            for seed in seeds:
                runs.append((proj, vname, vcfg.get("flags", []), seed))

    print(f"CoverAgent-ML Experiment Runner")
    print(f"================================")
    print(f"Projects:  {len(projects)} ({', '.join(p.name for p in projects)})")
    print(f"Variants:  {len(variants)} ({', '.join(variants.keys())})")
    print(f"Seeds:     {len(seeds)} ({seeds})")
    print(f"Total runs: {len(runs)}")
    print(f"Workspace:  {args.workspace}")
    print(f"Results:    {results_dir}")

    if args.dry_run:
        print("\n[DRY RUN] Planned runs:")
        for i, (proj, vname, vflags, seed) in enumerate(runs, 1):
            run_id = f"{proj.name}_{vname}_s{seed}"
            skip = ""
            if args.resume and (results_dir / f"{run_id}.json").exists():
                skip = " [SKIP: exists]"
            print(f"  {i:>3}. {run_id}{skip}")
        return

    # Execute runs
    all_results: List[RunResult] = []
    total = len(runs)
    t0_all = time.time()

    for i, (proj, vname, vflags, seed) in enumerate(runs, 1):
        run_id = f"{proj.name}_{vname}_s{seed}"

        # Resume support: skip if result already exists
        if args.resume and (results_dir / f"{run_id}.json").exists():
            print(f"\n[{i}/{total}] SKIP {run_id} (result exists)")
            with open(results_dir / f"{run_id}.json") as f:
                data = json.load(f)
            all_results.append(RunResult(**data))
            continue

        print(f"\n[{i}/{total}] Starting {run_id}...")
        result = run_single(
            proj, vname, vflags, seed,
            config, args.workspace, results_dir, logs_dir,
        )
        all_results.append(result)

        # Incremental summary
        write_summary_csv(all_results, summary_file)

        elapsed = time.time() - t0_all
        remaining_est = elapsed / i * (total - i)
        print(f"  [{i}/{total}] Elapsed: {elapsed:.0f}s, Est. remaining: {remaining_est:.0f}s")

    # Final summary
    print_summary_table(all_results)
    write_summary_csv(all_results, summary_file)

    total_time = time.time() - t0_all
    print(f"\nTotal experiment time: {total_time:.0f}s ({total_time/3600:.1f}h)")


if __name__ == "__main__":
    main()
