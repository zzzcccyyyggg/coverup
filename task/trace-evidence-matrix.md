# Trace Evidence Matrix

Date: 2026-03-26

## Core Judgment

The recovery loop is now strong enough that **plain coverage is no longer the right primary lens** for the paper.

Across the current targeted slices, the more informative distinction is:

- repair-assisted positive
- prompt-first positive
- repair-engaged but unsuccessful
- llm-only unsuccessful

That classification is closer to the actual method claim than raw final coverage alone.

## Matrix Source

Generated with:

```bash
python3 experiments/scripts/trace_matrix.py \
  /tmp/click-full-python-seg-v11.jsonl \
  /tmp/click-full-python-seg-v17.jsonl \
  /tmp/click-full-python-seg-v18.jsonl \
  /tmp/cobra-debugflags-v11.jsonl \
  /tmp/cobra-resetflags-v6.jsonl \
  /tmp/cobra-resetflags-v4.jsonl \
  /tmp/cobra-inithelp-v5.jsonl \
  /tmp/coverup-target-utils-noproxy.jsonl \
  --markdown
```

Script:

- [trace_matrix.py](/home/zzzccc/coverup/experiments/scripts/trace_matrix.py)

## Current Matrix

| Label | Segment | Attempts | Recovery Class | Observed Path | Last Cat | RepairEng | AvgPass | FixExh | Top Fixes |
| --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| click-full-python-seg-v11 | decorators.py:421-524 | 2 | repair-assisted positive | tool_repair+llm/F -> tool_repair+llm/G | unknown | 2 | 0.00 | 0 | python_fix_click_version_option_oracles |
| click-full-python-seg-v17 | decorators.py:421-524 | 3 | repair-engaged negative | tool_repair+llm/F x3 | syntax | 3 | 2.00 | 3 | python_reorder_version_option_args, python_fix_click_version_option_oracles |
| click-full-python-seg-v18 | decorators.py:421-524 | 2 | repair-assisted positive | tool_repair+llm/F -> tool_repair+llm/G | unknown | 2 | 1.50 | 1 | python_reorder_version_option_args, python_fix_click_version_option_oracles, python_fix_click_echo_patch_target |
| cobra-debugflags-v11 | command.go:1463-1499 | 1 | repair-assisted positive | tool_repair+llm/G | unknown | 1 | 1.00 | 0 | go_add_nonempty_output_helper, go_add_line_normalizer, go_add_normalized_contains_helper, go_add_debugflag_expectation_canonicalizer, go_normalize_actual_output_lines, go_normalize_expected_output_lines, go_iterate_normalized_expected_output, go_drop_position_sensitive_contains_asserts |
| cobra-resetflags-v6 | command.go:1749-1759 | 1 | prompt-first positive | llm/G | unknown | 0 | 0.00 | 0 | - |
| cobra-resetflags-v4 | command.go:1749-1759 | 3 | repair-engaged negative | tool_repair+llm/F x3 | assertion | 3 | 0.33 | 3 | go_remove_invalid_output_accessor_assert |
| cobra-inithelp-v5 | command.go:1232-1277 | 1 | repair-engaged negative | tool_repair+llm/F | assertion | 1 | 1.00 | 1 | go_add_nonempty_output_helper, go_add_line_normalizer, go_add_normalized_contains_helper, go_add_debugflag_expectation_canonicalizer, go_normalize_contains_output_asserts |
| coverup-target-utils-noproxy | utils.rs:150-191 | 2 | prompt-first positive | llm/F -> llm/G | unknown | 0 | 0.00 | 0 | - |

## What This Supports

### 1. The Same Loop Produces Different Recovery Classes

- Python:
  - `click v11`, `click v18` are repair-assisted positive
  - `click v17` is repair-engaged negative
- Go:
  - `DebugFlags v11` is repair-assisted positive
  - `ResetFlags v6` is prompt-first positive
  - `ResetFlags v4` and `InitDefaultHelpCmd v5-v8` are repair-engaged negative
- Rust:
  - `utils.rs:150-191` is prompt-first positive

This means the paper should not collapse all successful slices into one bucket, and it also should not describe each language with a single scalar maturity label.

### 2. The Cross-Language Story Is Getting More Defensible

The matrix now supports a sharper statement:

- repair-assisted positives exist in more than one language family
- prompt-first positives also exist in more than one language family
- repair-engaged negatives remain visible in both Python and Go

So the paper can more credibly argue that:

- the same orchestration loop is real across languages
- but the effective recovery path depends on operator maturity and failure family

### 3. Go Is No Longer A Binary Story

Go still provides the richest within-language contrast:

- prompt-first success
- repair-assisted success
- repair-engaged failure
- behavior-semantics failure probe with visible frontier movement across `InitDefaultHelpCmd v5-v8`

That is a stronger systems story than “Go works” vs “Go does not work”.

### 4. Fixpoint Metrics Matter

The matrix makes three trace-derived fields immediately useful:

- `RepairEng`
- `AvgPass`
- `FixExh`

These are already more diagnostic than final coverage for explaining why a slice improved or stalled.

### 5. Baseline Sanity Now Exists

The project now has a small paired baseline sanity set:

- [baseline-sanity-audit.md](/home/zzzccc/coverup/task/baseline-sanity-audit.md)

That new contrast adds an important boundary:

- `click` and `DebugFlags` look like slices where the full recovery loop matters
- `ResetFlags` still looks prompt-first even under baseline
- `InitDefaultHelpCmd` now gives a harder paired contrast where the full loop changes the recovery class but not yet the outcome
- Rust `utils.rs:150-191` now extends the baseline sanity story to the hardest language, with a prompt-first full positive versus llm-only baseline negative

So the paper should not frame every positive slice as a repair-dependent win.

## Risks

- This is still a small targeted matrix, not a full experiment table.
- Some related traces are interrupted probes, even though the current matrix now only keeps the most informative observed row from that family.
- `Last Cat = unknown` on positive slices means the current trace schema is still better at failure explanation than success explanation.
- The Rust row is a prompt-first targeted positive, not evidence that Rust bounded repair is mature.

## Most Valuable Next Step

Turn this matrix into the paper's first trace-driven mechanism table, then add:

1. one more Python slice
2. one more Go slice
3. one more Rust slice, ideally one negative-to-positive or repair-engaged case
4. one more paired contrast beyond the current baseline sanity set

At that point, the paper can evaluate:

- not only whether the system improved
- but **how it improved**
