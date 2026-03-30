# Compact Method Exploration Audit

Date: 2026-03-25

Scope:
- project: `similar`
- targeted segment: `src/algorithms/compact.rs:248-350`
- goal: understand which retry/control strategy is actually promising on a hard Rust segment

## Core Judgment

We now have three concrete results on the same hard segment:

1. semantic recovery `on`
2. semantic recovery `off`
3. a new `coverage-stall mode` that forces blocker-first, minimal-test behavior after repeated useless retries

The current evidence says:

- semantic recovery changes the live prompt path, but did not improve outcome on this slice
- coverage-stall mode is **not** the next winning method; in this run it was worse, because the segment never reached the repeated-`U` state where that mode helps
- the more promising next direction is **compile-shape recovery**, not more semantic coverage guidance

## Facts

### 1. Semantic Recovery ON

Artifacts:

- [coverup-target-compact-semantic.jsonl](/tmp/coverup-target-compact-semantic.jsonl)
- [coverup-target-compact-semantic.log](/tmp/coverup-target-compact-semantic.log)

Observed outcome:

- `F=1, U=2, G=0`
- `83.4% -> 83.4%`

Important evidence:

- the third live prompt contains `Semantic recovery mode:`
- it explicitly says the segment stalled for `2` recent attempts without a new `G`

Interpretation:

- the semantic branch is real and reachable
- but on this slice it did not convert into coverage gain

### 2. Semantic Recovery OFF

Artifacts:

- [coverup-target-compact-no-semantic-full.jsonl](/tmp/coverup-target-compact-no-semantic-full.jsonl)
- [coverup-target-compact-no-semantic-full.log](/tmp/coverup-target-compact-no-semantic-full.log)

Observed outcome:

- `F=1, U=2, G=0`
- `83.4% -> 83.4%`

Important evidence:

- summary JSON records `"semantic_recovery_enabled": false`
- the log does **not** contain `Semantic recovery mode:`

Interpretation:

- the flag changes the live prompt path cleanly
- but again, no outcome gain on this slice

### 3. Coverage-Stall Mode

Implementation idea:

- after repeated `U`, force the model to:
  - write at most `1-2` tests
  - target blocker `#1` only
  - translate blocker conditions directly into input shape

Artifacts:

- [coverup-target-compact-stallmode.jsonl](/tmp/coverup-target-compact-stallmode.jsonl)
- [coverup-target-compact-stallmode.log](/tmp/coverup-target-compact-stallmode.log)

Observed outcome:

- `F=3, U=0, G=0`
- `83.4% -> 83.4%`
- error shape was compile-dominated:
  - repeated `E0061`
  - repeated incorrect `diff_slices(...)` usage
  - repeated `.unwrap()` on non-`Result`
  - trait-method visibility issues such as `finish`

Interpretation:

- this method did not help on this run
- more importantly, it attacked the wrong failure layer
- the segment never entered the repeated-coverage-stall shape where blocker-first minimality could matter

## Strong Inferences

- The current bottleneck on this `compact` slice is not primarily “the model needs stronger coverage targeting.”
- The current bottleneck is “the model keeps hallucinating API shape and trait usage.”
- Therefore, a more promising next method is:
  - compile-shape recovery
  - signature grounding
  - explicit trait-import / return-type / helper-signature correction

## Submitability Audit

### Novelty Audit

- semantic recovery remains potentially publishable as part of an adaptive retry controller
- coverage-stall mode, in its current form, is not yet evidence-backed

### Methodology Audit

- strongly improved
- we now have causal targeted slices and can reject method candidates instead of arguing abstractly

### Evaluation Audit

- improved
- this is not just “one run succeeded / failed”
- it is already enough to say which class of methods is underperforming

### Writing Audit

- paper-safe claim:
  - “We used targeted ablations to identify when retry-time guidance changes behavior and when it does not.”
- unsafe claim:
  - “Our blocker-first semantic mode improves hard Rust segments.”

## Most Valuable Next Step

Do **not** keep investing in stronger coverage-stall wording until compile-shape errors are controlled.

The next method to explore should be a `compile-shape recovery` mode that activates after repeated Rust compile failures like:

- `E0061`
- `E0599`
- `E0624`
- signature/trait-import misuse around public wrappers vs hook-style APIs

That is the most evidence-backed next bet.
