# CoverAgent-ML: Experiment Design & Reproduction Guide

## Overview

This document describes the experiment setup for evaluating CoverAgent-ML,
a verification-driven multi-language test generation framework that augments
CoverUp with Diagnostic IR, Reflective Memory, and Tool-First Repair.

## Research Questions

- **RQ1 (Effectiveness)**: Does CoverAgent-ML improve test generation success rate
  and final coverage compared to vanilla CoverUp?
- **RQ2 (Ablation)**: What is the contribution of each agent module
  (Memory, Repair, Planner, Blocker)?
- **RQ3 (Cross-language)**: How do the agent modules generalize across
  Rust, Python, and Go?
- **RQ4 (Efficiency)**: Does CoverAgent-ML reduce LLM API cost while
  maintaining or improving coverage?

## Experiment Matrix

| Dimension | Values | Count |
|-----------|--------|-------|
| Projects  | similar, semver, strsim-rs (Rust); flask, click, pydantic (Python); cobra, logrus, gjson (Go) | 9 |
| Seeds     | 42, 123, 456 | 3 |
| Variants  | full, no_memory, no_repair, no_planner, no_blocker, baseline | 6 |
| **Total** | | **162 runs** |

## Variants (Ablation)

| Variant | Description | CLI Flags |
|---------|-------------|-----------|
| `full` | Full CoverAgent-ML | (none) |
| `no_memory` | Disable ReflectiveMemory | `--no-agent-memory` |
| `no_repair` | Disable tool-first repair | `--no-agent-repair` |
| `no_planner` | Disable UCB planner | `--no-agent-planner` |
| `no_blocker` | Disable coverage blocker explanation | `--no-agent-blocker` |
| `baseline` | Vanilla CoverUp (all disabled) | `--no-agent-memory --no-agent-repair --no-agent-planner --no-agent-blocker` |

## Metrics

### Primary
- **Good (G)**: Number of segments with successful test generation
- **Line Coverage (%)**: Final line coverage after all tests
- **Branch Coverage (%)**: Final branch coverage (when available)
- **Cost ($)**: Total LLM API cost per run

### Secondary
- **Failed (F)**: Total failed attempts (lower is more efficient)
- **Useless (U)**: Tests that compiled but didn't improve coverage
- **Wall Time (s)**: Total execution time
- **Memory Lessons**: Number of episodic memory entries accumulated
- **Repair Fixes**: Number of tool-first repairs attempted/succeeded

### Derived
- **Success Rate**: G / total_segments
- **Efficiency**: G / (G + F + U) — fraction of attempts that succeed
- **Cost per Good**: Cost / G — API cost per successful test

## Project Selection Criteria

1. **Diversity**: Cover three languages with different type systems
2. **Size**: Small-medium (500–5000 LOC) for feasible experiments
3. **Test Infrastructure**: Projects with existing test suites for baseline
4. **Public & Reproducible**: Open-source with tagged releases

## Configuration

### LLM
- Model: `deepseek/deepseek-coder`
- Temperature: 0 (deterministic)
- Max concurrency: 5
- Max attempts per segment: 5

### Coverage Tools
- Rust: `cargo-llvm-cov --json`
- Python: `slipcover` + `pytest`
- Go: `go test -coverprofile`

## How to Run

### Prerequisites
```bash
pip install pyyaml  # for config parsing
cargo install cargo-llvm-cov  # for Rust
```

### Single Project
```bash
cd /path/to/coverup
python3 experiments/scripts/run_experiments.py \
    --project similar --variant full no_blocker baseline --seed 42
```

### Full Matrix
```bash
python3 experiments/scripts/run_experiments.py
```

### Resume After Interruption
```bash
python3 experiments/scripts/run_experiments.py --resume
```

### Analyze Results
```bash
# ASCII table
python3 experiments/scripts/analyze_results.py

# LaTeX table for paper
python3 experiments/scripts/analyze_results.py --latex

# Ablation deltas
python3 experiments/scripts/analyze_results.py --ablation

# Log analysis
python3 experiments/scripts/analyze_log.py experiments/logs/similar_full_s42.log
```

## Expected Results Pattern

Based on A/B experiments on `similar` crate (Rust, 58 segments, initial 81.0%):

| Variant | G | F | U | Coverage | Cost | Time |
|---------|---|---|---|----------|------|------|
| Full (Agent v2) | 23 | 110 | 15 | **92.5%** | ~$0.35 | ~44 min |
| Baseline (no agent) | 31 | 173 | 6 | 90.9% | ~$0.39 | ~40 min |

Key observations (Agent v2 with P0-P4 improvements):
- Agent achieves +1.6pp higher coverage with 30% fewer LLM calls
- Planner selects higher-value segments: 23 G → 92.5%, vs Baseline 31 G → 90.9%
- Memory accumulated 26 recipes; `unknown` category highest success (23/32)
- Planner: 147 pulls across 58 arms, plateau detection frozen low-yield segments
- Tool-first repair triggers on all compilation failures via cargo check JSON
- Agent v1 (pre-P0-P4) was **negative** (-1.4pp vs baseline); v2 is **positive** (+1.6pp)

### Version History

| Version | Agent Cov | Baseline Cov | Delta | Notes |
|---------|-----------|--------------|-------|-------|
| v1 (pre-P0-P4) | 92.0% | 93.4% | -1.4pp | Memory=frequency chart, Planner never called |
| **v2 (P0-P4)** | **92.5%** | **90.9%** | **+1.6pp** | Recipe memory, batch planner, cargo check autofix |

## File Structure

```
scripts/
    experiment_config.yaml   # Project/variant/seed configuration
    run_experiments.py       # Main experiment runner
    analyze_results.py       # Result aggregation & table generation
    analyze_log.py           # Log file analysis
experiments/
    results/                 # Per-run JSON files
    logs/                    # Per-run CoverUp log files
    summary.csv              # Aggregated CSV
docs/
    experiment_design.md     # This document
```
