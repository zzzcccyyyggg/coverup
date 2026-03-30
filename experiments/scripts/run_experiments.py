#!/usr/bin/env python3
"""
CoverAgent-ML Experiment Runner
================================
Runs the full experiment matrix: projects × seeds × ablation variants.
Collects results into CSV for analysis.

Usage:
    python experiments/scripts/run_experiments.py                           # full run
    python experiments/scripts/run_experiments.py --project similar         # single project
    python experiments/scripts/run_experiments.py --variant full baseline   # specific variants
    python experiments/scripts/run_experiments.py --seed 42                 # single seed
    python experiments/scripts/run_experiments.py --dry-run                 # plan only
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = Path(__file__).resolve().with_name("experiment_config.yaml")


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
    initial_line_coverage: float = 0.0
    good: int = 0
    failed: int = 0
    useless: int = 0
    total_segments: int = 0
    line_coverage: float = 0.0
    coverage_delta: float = 0.0
    branch_coverage: float = 0.0
    cost_usd: float = 0.0
    wall_time_sec: float = 0.0
    memory_lessons: int = 0
    repair_tool_fixes: int = 0
    planner_pulls: int = 0
    log_file: str = ""
    trace_file: str = ""
    stdout_file: str = ""
    return_code: int = 0
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "project": self.project,
            "language": self.language,
            "variant": self.variant,
            "seed": self.seed,
            "initial_line_coverage": self.initial_line_coverage,
            "good": self.good,
            "failed": self.failed,
            "useless": self.useless,
            "total_segments": self.total_segments,
            "line_coverage": self.line_coverage,
            "coverage_delta": self.coverage_delta,
            "branch_coverage": self.branch_coverage,
            "cost_usd": self.cost_usd,
            "wall_time_sec": self.wall_time_sec,
            "memory_lessons": self.memory_lessons,
            "repair_tool_fixes": self.repair_tool_fixes,
            "planner_pulls": self.planner_pulls,
            "log_file": self.log_file,
            "trace_file": self.trace_file,
            "stdout_file": self.stdout_file,
            "return_code": self.return_code,
            "error": self.error,
        }


class ProjectPreparationError(RuntimeError):
    """Raised when a benchmark project cannot be cloned or prepared."""


# ── Helpers ─────────────────────────────────────────────────────────────

def load_config(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def ensure_project(proj: ProjectConfig, workspace: Path) -> Path:
    """Clone and checkout the project if needed. Returns project dir."""
    proj_dir = workspace / proj.name
    if proj_dir.exists():
        print(f"  [skip] {proj.name} already cloned at {proj_dir}")
        return proj_dir

    print(f"  [clone] {proj.name} from {proj.repo} @ {proj.tag}")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", proj.tag, proj.repo, str(proj_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        details = "\n".join(
            part.strip()
            for part in (exc.stdout or "", exc.stderr or "")
            if part and part.strip()
        )
        if not details:
            details = str(exc)
        raise ProjectPreparationError(
            f"git clone failed for {proj.name} @ {proj.tag}: {details}"
        ) from exc
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


def save_result_json(result: RunResult, results_dir: Path) -> Path:
    """Persist a single run result and return the JSON path."""
    result_file = results_dir / f"{result.project}_{result.variant}_s{result.seed}.json"
    with open(result_file, "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    return result_file


def build_coverup_cmd(
    proj: ProjectConfig,
    proj_dir: Path,
    variant_flags: List[str],
    seed: int,
    config: dict,
    log_file: Path,
    trace_file: Path,
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
        "--trace-log", str(trace_file),
        "--seed", str(seed),
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
    summary_match = re.search(r'^\[CoverUp\] Summary JSON:\s*(\{.*\})$', output, re.MULTILINE)
    if summary_match:
        try:
            summary = json.loads(summary_match.group(1))
        except json.JSONDecodeError:
            summary = None
        if summary:
            counters = summary.get("counters", {})
            result["good"] = counters.get("G", 0)
            result["failed"] = counters.get("F", 0)
            result["useless"] = counters.get("U", 0)
            result["total_segments"] = summary.get("segments_total", 0)
            result["initial_line_coverage"] = summary.get("initial_coverage", 0.0) or 0.0
            result["line_coverage"] = summary.get("final_coverage", 0.0) or 0.0
            result["cost_usd"] = summary.get("cost_usd", 0.0) or 0.0
            result["memory_lessons"] = summary.get("memory_lessons", 0) or 0
            result["planner_pulls"] = summary.get("planner_pulls", 0) or 0

    # Parse final progress bar line: G=XX, F=XX, U=XX
    m = re.search(r'G=(\d+),\s*F=(\d+),\s*U=(\d+)', output)
    if m and "good" not in result:
        result["good"] = int(m.group(1))
        result["failed"] = int(m.group(2))
        result["useless"] = int(m.group(3))

    # Parse total segments from progress bar: XX/YY
    m = re.search(r'(\d+)/(\d+)\s*\[', output)
    if m and "total_segments" not in result:
        result["total_segments"] = int(m.group(2))

    # Parse cost
    m = re.search(r'cost=~\$([0-9.]+)', output)
    if m and "cost_usd" not in result:
        result["cost_usd"] = float(m.group(1))

    # Parse labelled coverage emitted by CoverUp.
    m = re.search(r'^\[CoverUp\] Initial coverage:\s*([0-9.]+)%$', output, re.MULTILINE)
    if m and "initial_line_coverage" not in result:
        result["initial_line_coverage"] = float(m.group(1))

    m = re.search(r'^\[CoverUp\] Final coverage:\s*([0-9.]+)%$', output, re.MULTILINE)
    if m and "line_coverage" not in result:
        result["line_coverage"] = float(m.group(1))

    # Fallback: use the first/last bare percentages printed after suite measurement.
    if "initial_line_coverage" not in result or "line_coverage" not in result:
        coverage_values = [
            float(match.group(1))
            for match in re.finditer(r'^Measuring coverage\.\.\.\s+([0-9.]+)%$', output, re.MULTILINE)
        ]
        if coverage_values:
            result.setdefault("initial_line_coverage", coverage_values[0])
            result.setdefault("line_coverage", coverage_values[-1])

    # Parse agent stats from [CoverAgent-ML] output
    m = re.search(r'Memory:\s*(\d+)\s*lessons', output)
    if m and "memory_lessons" not in result:
        result["memory_lessons"] = int(m.group(1))

    m = re.search(r'Planner:\s*(\d+)\s*pulls', output)
    if m and "planner_pulls" not in result:
        result["planner_pulls"] = int(m.group(1))

    # Count tool-first repairs from log
    if log_file.exists():
        log_text = log_file.read_text(errors="ignore")
        result["repair_tool_fixes"] = log_text.count("[REPAIR] Tool-first fixes applied")

    result.setdefault("initial_line_coverage", 0.0)
    result.setdefault("line_coverage", 0.0)
    result.setdefault("branch_coverage", 0.0)
    result["coverage_delta"] = round(
        result["line_coverage"] - result["initial_line_coverage"], 3
    )

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
    traces_dir: Path,
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

    # Log file for this run
    log_file = logs_dir / f"{run_id}.log"
    trace_file = traces_dir / f"{run_id}.jsonl"
    stdout_file = logs_dir / f"{run_id}.stdout.log"
    result.log_file = str(log_file)
    result.trace_file = str(trace_file)
    result.stdout_file = str(stdout_file)

    try:
        proj_dir = ensure_project(proj, workspace)
        clean_generated_tests(proj_dir, proj.language)
    except Exception as e:
        result.return_code = -1
        result.error = f"setup_failed: {str(e)[:200]}"
        result.wall_time_sec = 0.0
        setup_error = f"[SETUP ERROR] {e}\n"
        stdout_file.write_text(setup_error)
        log_file.write_text(setup_error)
        save_result_json(result, results_dir)
        print(f"  [SETUP ERROR] {e}")
        print(f"  Error: {result.error}")
        return result

    # Build command
    cmd = build_coverup_cmd(proj, proj_dir, variant_flags, seed, config, log_file, trace_file)

    # Set up environment
    env = os.environ.copy()
    repo_src = str(REPO_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        repo_src if not existing_pythonpath
        else repo_src + os.pathsep + existing_pythonpath
    )
    env["PYTHONHASHSEED"] = str(seed)
    env["COVERUP_EXPERIMENT_SEED"] = str(seed)

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
            cwd=str(proj_dir),
        )
        wall_time = time.time() - t0
        output = proc.stdout + proc.stderr
        stdout_file.write_text(output)
        result.return_code = proc.returncode

        # Parse metrics from output
        metrics = parse_output(output, log_file)
        result.initial_line_coverage = metrics.get("initial_line_coverage", 0.0)
        result.good = metrics.get("good", 0)
        result.failed = metrics.get("failed", 0)
        result.useless = metrics.get("useless", 0)
        result.total_segments = metrics.get("total_segments", 0)
        result.line_coverage = metrics.get("line_coverage", 0.0)
        result.coverage_delta = metrics.get("coverage_delta", 0.0)
        result.branch_coverage = metrics.get("branch_coverage", 0.0)
        result.cost_usd = metrics.get("cost_usd", 0.0)
        result.wall_time_sec = wall_time
        result.memory_lessons = metrics.get("memory_lessons", 0)
        result.repair_tool_fixes = metrics.get("repair_tool_fixes", 0)
        result.planner_pulls = metrics.get("planner_pulls", 0)

        if proc.returncode != 0:
            result.error = f"exit_code={proc.returncode}"

    except subprocess.TimeoutExpired as exc:
        partial_output = (exc.stdout or "") + (exc.stderr or "")
        if partial_output:
            stdout_file.write_text(partial_output)
        wall_time = time.time() - t0
        result.wall_time_sec = wall_time
        result.return_code = -1
        result.error = "timeout"
        print(f"  [TIMEOUT] after {wall_time:.0f}s")

    except Exception as e:
        stdout_file.write_text(f"[RUN ERROR] {e}\n")
        wall_time = time.time() - t0
        result.wall_time_sec = wall_time
        result.return_code = -1
        result.error = str(e)[:200]
        print(f"  [ERROR] {e}")

    save_result_json(result, results_dir)

    print(f"  Result: G={result.good}, F={result.failed}, U={result.useless}")
    print(
        f"  Coverage: initial={result.initial_line_coverage:.1f}%, "
        f"final={result.line_coverage:.1f}%, delta={result.coverage_delta:+.1f}pp"
    )
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

    print(f"\n{'='*96}")
    print(f"{'Project':<12} {'Variant':<12} {'Seed':>4} {'G':>4} {'F':>4} {'U':>4} "
          f"{'Init%':>7} {'Final%':>7} {'Delta':>7} {'Cost':>7} {'Time':>6} {'Mem':>4} {'Rep':>4} {'Err':>4}")
    print(f"{'-'*96}")

    for r in sorted(results, key=lambda x: (x.project, x.variant, x.seed)):
        print(f"{r.project:<12} {r.variant:<12} {r.seed:>4} {r.good:>4} {r.failed:>4} {r.useless:>4} "
              f"{r.initial_line_coverage:>6.1f}% {r.line_coverage:>6.1f}% {r.coverage_delta:>+6.1f} "
              f"${r.cost_usd:>5.3f} {r.wall_time_sec:>5.0f}s {r.memory_lessons:>4} {r.repair_tool_fixes:>4} "
              f"{'yes' if r.error else 'no':>4}")

    print(f"{'='*96}")


def main():
    ap = argparse.ArgumentParser(
        description="CoverAgent-ML Experiment Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
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
    config_path = args.config if args.config.is_absolute() else (REPO_ROOT / args.config)
    config = load_config(config_path)
    api_key_env = config.get("llm", {}).get("api_key_env", "DEEPSEEK_API_KEY")

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
    results_dir = REPO_ROOT / Path(config["output"]["results_dir"])
    logs_dir = REPO_ROOT / Path(config["output"]["logs_dir"])
    traces_dir = REPO_ROOT / Path(config["output"].get("traces_dir", "experiments/traces"))
    summary_file = REPO_ROOT / Path(config["output"]["summary_file"])

    results_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    traces_dir.mkdir(parents=True, exist_ok=True)
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
    if api_key_env not in os.environ:
        print(f"Warning: {api_key_env} is not set in the current environment; model-backed runs may fail.")

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
            config, args.workspace, results_dir, logs_dir, traces_dir,
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
