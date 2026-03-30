# Baseline Sanity Audit

Date: 2026-03-26

## Core Judgment

The project now has a **small but defensible baseline sanity set**.

That set already supports a sharper and more honest paper claim:

- some targeted gains really do require the full recovery loop
- some simpler targeted gains remain prompt-first even under baseline

This is useful because it prevents us from over-claiming that every positive slice needs the full method.

## Matrix Source

Generated with:

```bash
python3 experiments/scripts/trace_matrix.py \
  /tmp/click-full-python-seg-v18.jsonl \
  /tmp/click-baseline-seg-v2.jsonl \
  /tmp/cobra-debugflags-v11.jsonl \
  /tmp/cobra-debugflags-baseline-v1.jsonl \
  /tmp/cobra-resetflags-v6.jsonl \
  /tmp/cobra-resetflags-baseline-v1.jsonl \
  /tmp/cobra-inithelp-v5.jsonl \
  /tmp/cobra-inithelp-baseline-v1.jsonl \
  /tmp/coverup-target-utils-noproxy.jsonl \
  /tmp/rust-utils-baseline-v2.jsonl \
  --markdown
```

Script:

- [trace_matrix.py](/home/zzzccc/coverup/experiments/scripts/trace_matrix.py)

Baseline variant used:

- `--no-agent-memory`
- `--no-agent-repair`
- `--no-agent-planner`
- `--no-agent-blocker`

## Baseline Matrix

| Label | Segment | Attempts | Recovery Class | Observed Path | Last Cat | RepairEng | AvgPass | FixExh | Top Fixes |
| --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| click-full-python-seg-v18 | decorators.py:421-524 | 2 | repair-assisted positive | tool_repair+llm/F -> tool_repair+llm/G | unknown | 2 | 1.50 | 1 | python_reorder_version_option_args, python_fix_click_version_option_oracles, python_fix_click_echo_patch_target |
| click-baseline-seg-v2 | decorators.py:420-530 | 3 | llm-only negative | llm/F x3 | visibility | 0 | 0.00 | 0 | - |
| cobra-debugflags-v11 | command.go:1463-1499 | 1 | repair-assisted positive | tool_repair+llm/G | unknown | 1 | 1.00 | 0 | go_add_nonempty_output_helper, go_add_line_normalizer, go_add_normalized_contains_helper, go_add_debugflag_expectation_canonicalizer, go_normalize_actual_output_lines, go_normalize_expected_output_lines, go_iterate_normalized_expected_output, go_drop_position_sensitive_contains_asserts |
| cobra-debugflags-baseline-v1 | command.go:1463-1499 | 2 | llm-only negative | llm/F x2 | assertion | 0 | 0.00 | 0 | - |
| cobra-resetflags-v6 | command.go:1749-1759 | 1 | prompt-first positive | llm/G | unknown | 0 | 0.00 | 0 | - |
| cobra-resetflags-baseline-v1 | command.go:1749-1759 | 2 | prompt-first positive | llm/F -> llm/G | unknown | 0 | 0.00 | 0 | - |
| cobra-inithelp-v5 | command.go:1232-1277 | 1 | repair-engaged negative | tool_repair+llm/F | assertion | 1 | 1.00 | 1 | go_add_nonempty_output_helper, go_add_line_normalizer, go_add_normalized_contains_helper, go_add_debugflag_expectation_canonicalizer, go_normalize_contains_output_asserts |
| cobra-inithelp-baseline-v1 | command.go:1232-1277 | 2 | llm-only negative | llm/F x2 | assertion | 0 | 0.00 | 0 | - |
| coverup-target-utils-noproxy | utils.rs:150-191 | 2 | prompt-first positive | llm/F -> llm/G | unknown | 0 | 0.00 | 0 | - |
| rust-utils-baseline-v2 | utils.rs:150-191 | 2 | llm-only negative | llm/F x2 | panic | 0 | 0.00 | 0 | - |

## Pairwise Reading

### 1. Python `click` `version_option`

Facts:

- Full current-stack run is a repair-assisted positive:
  - `/tmp/click-full-python-seg-v18.jsonl`
- Baseline run is an llm-only negative:
  - `/tmp/click-baseline-seg-v2.jsonl`

Observed difference:

- full path:
  - `tool_repair+llm/F -> tool_repair+llm/G`
- baseline path:
  - `llm/F x3`

Why this matters:

- On this slice, the gain is not plausibly explained by plain prompt retries.
- The baseline failures stay trapped in syntax and visibility families.
- The full loop is what moves the slice into a successful terminal outcome.

Boundary:

- The baseline segment is reported as `decorators.py:420-530` while the full trace is `421-524`.
- This is still the same `version_option` target family, so it is acceptable for sanity evidence, but it is not a perfect line-matched pair.

### 2. Go `DebugFlags`

Facts:

- Full current-stack run is a repair-assisted positive:
  - `/tmp/cobra-debugflags-v11.jsonl`
- Baseline run is an llm-only negative:
  - `/tmp/cobra-debugflags-baseline-v1.jsonl`

Observed difference:

- full path:
  - `tool_repair+llm/G`
- baseline path:
  - `llm/F x2`

Why this matters:

- This is the cleanest non-Python baseline contrast we currently have.
- The positive result is not just “Go can work”; it is specifically a case where the recovery layer explains the difference.

### 3. Go `ResetFlags`

Facts:

- Full current-stack run is prompt-first positive:
  - `/tmp/cobra-resetflags-v6.jsonl`
- Baseline run is also prompt-first positive:
  - `/tmp/cobra-resetflags-baseline-v1.jsonl`

Observed difference:

- full path:
  - `llm/G`
- baseline path:
  - `llm/F -> llm/G`

Why this matters:

- This slice does **not** need the full loop to recover.
- That is actually a useful result for the paper because it shows the method is not being credited for every gain.
- `ResetFlags` is a simpler slice and should be presented as a prompt-first positive, not as a repair-assisted success.

### 4. Go `InitDefaultHelpCmd`

Facts:

- Full current-stack run is repair-engaged negative:
  - `/tmp/cobra-inithelp-v5.jsonl`
- Baseline run is llm-only negative:
  - `/tmp/cobra-inithelp-baseline-v1.jsonl`
- Later full-only reruns deepened the same family without changing the paired classification:
  - `/tmp/cobra-inithelp-v6.jsonl`
  - `/tmp/cobra-inithelp-v7.jsonl`
  - `/tmp/cobra-inithelp-v8.jsonl`

Observed difference:

- full path:
  - `tool_repair+llm/F`
- baseline path:
  - `llm/F x2`

Why this matters:

- This is the first harder paired baseline contrast in the Go behavior-semantics family.
- It does **not** show effectiveness gain yet.
- It does show that the full loop changes the recovery class even before the slice turns positive.
- That is useful mechanism evidence because the harder slice is no longer just “failed either way”; it failed differently.
- The later `v6-v8` reruns make that mechanism story stronger:
  - the slice did not merely stay `repair-engaged negative`
  - it also moved from shallow output-format errors toward deeper `Find(args)` / `Args` semantics and helper-process exit/output semantics

### 5. Rust `TextDiffRemapper` (`utils.rs:150-191`)

Facts:

- Full current-stack run is prompt-first positive:
  - `/tmp/coverup-target-utils-noproxy.jsonl`
- Baseline run is llm-only negative:
  - `/tmp/rust-utils-baseline-v2.jsonl`

Observed difference:

- full path:
  - `llm/F -> llm/G`
- baseline path:
  - `llm/F x2`

Why this matters:

- This is the first Rust paired baseline contrast in the sanity set.
- It extends the baseline story to the hardest language family.
- The difference is not repair-assisted; both traces are still `llm`-only.
- That means this slice is useful for a different paper point:
  - some hardest-language gains may depend on the broader full stack
  - even when they do not yet depend on tool repair

## What This Supports

1. The baseline story is now partially grounded, not hypothetical.

2. The full system matters on at least three targeted slices:
   - Python `click`
   - Go `DebugFlags`
   - Rust `utils.rs:150-191`

3. Some slices remain simpler and prompt-first:
   - Go `ResetFlags`

4. Harder negative pairs are now informative too:
   - Go `InitDefaultHelpCmd` is repair-engaged under the full loop but llm-only under baseline

5. The baseline sanity set now spans Python, Go, and Rust.

6. The right evaluation lens is now:
   - not only final coverage
   - but also whether the terminal path is `llm-only`, `prompt-first`, `repair-engaged`, or `repair-assisted`

## Risks

- This is still a very small targeted sanity set.
- The Python pair is function-matched rather than perfectly line-matched.
- `InitDefaultHelpCmd` only strengthens the mechanism story, not the effectiveness story.
- The Rust pair only shows that the broader full stack matters on this slice; it does not show Rust repair maturity.
- These results are strong sanity evidence, not yet a full baseline section for the final paper.

## Most Valuable Next Step

Extend the same paired sanity logic to one more nontrivial slice, ideally:

1. one more negative-to-positive paired contrast beyond the current Go/Rust set
2. or one harder behavior-semantics slice that turns repair-engaged negative into repair-assisted positive

That would let the paper say not only that baseline matters in principle, but that the recovery-class contrast persists beyond the current easiest comparison set.
