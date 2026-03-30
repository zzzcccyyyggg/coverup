# `similar` Patched Full Partial Smoke Audit

Date: 2026-03-25

Scope:
- project: `similar`
- seed: `42`
- variant: patched `full`
- output root: `/tmp/coveragent-similar-full`
- workspace: `/tmp/coveragent-similar-workspace`
- run status: manually interrupted before completion

Important limitation:
- This file records partial evidence from the in-progress trace.
- It does **not** provide a final coverage result and must not be cited as a completed experiment outcome.

## Core Judgment

This run is valuable as a qualitative counterpoint to `strsim-rs`.

`similar` is a Rust 2018 crate, so it does not share `strsim-rs`'s implicit Rust 2015 import gate. The partial trace shows that:

- the system is not dead-on-arrival on Rust 2018,
- but its main bottlenecks shift to compile-failure handling for `panic`, `visibility`, `type`, and `ownership` errors,
- and unlike `strsim-rs`, tool repair and memory both begin to participate.

So the current evidence supports a two-layer story:

1. `strsim-rs` recovery mainly demonstrated removal of a language/build compatibility gate.
2. `similar` demonstrates that after such gates are absent, the next bottleneck is compile-failure absorption and high-cost reasoning/tool churn.

## Facts Supported by the Partial Trace

From `/tmp/coveragent-similar-full/traces/similar_full_s42.jsonl` at interruption time:

- total attempts observed: `38`
- outcomes: `4 G / 28 F / 6 U`
- segments attempted: `10`
- segments good: `4`
- segments failed: `9`
- segments useless: `4`

Diagnostic composition:

- `panic`: `15`
- `unknown`: `10`
- `type`: `7`
- `visibility`: `5`
- `ownership`: `1`

Top observed error codes:

- `E0061 x4`
- `E0603 x3`
- `E0624 x2`
- `E0277 x2`
- `E0716 x1`
- `E0308 x1`

Prompt/runtime behavior:

- memory injected attempts: `19`
- blocker injected attempts: `29`
- tool repair attempts: `3`
- tool repair full successes: `2`
- tool repair partial/fallback: `1`
- observed fix type: `cargo_autofix(mismatched_lifetime_syntaxes)`

Concrete trace examples:

- first observed `G` on `src/types.rs:340-377`
- ownership compile failure `E0716` on `src/utils.rs:150-191`
- repeated visibility failures (`E0603`, `E0624`) on `src/algorithms/lcs.rs` and `src/udiff.rs`
- successful tool-repair-assisted `G` on `src/udiff.rs:255-272`

## Strong Inferences

- `similar` does not look like another `strsim-rs`-style import-gate failure.
- The system can make progress on Rust 2018 without the special `extern crate` fix.
- The next real bottleneck is compile-failure handling for richer Rust diagnostics, especially:
  - private item access
  - wrong function signatures
  - trait/type mismatches
  - panic-like compile/runtime failures
- Tool repair becomes non-trivial on this project, unlike `strsim-rs`.

## What This Does and Does Not Support

Supported:

- `strsim-rs` should not be treated as the whole Rust story.
- Repair is not globally inert; it begins to help on `similar`.
- Memory also starts to matter on `similar`, unlike the original `strsim-rs` runs.

Not supported:

- any final statement about `similar` coverage gain
- any ranking between `full`, `no_planner`, and `no_blocker` on `similar`
- any claim that the current Rust stack is submission-ready across Rust benchmarks

## Most Valuable Next Steps

1. Re-run `similar/full` to completion.
   - We need a completed result JSON before using it in any paper-facing table.

2. Add a repair audit for Rust compile failures beyond import handling.
   - Priority categories from this trace: `visibility`, `type`, and `ownership`.

3. Consider targeted tool fixes for:
   - private-item misuse (`E0603`, `E0624`)
   - wrong-arity / wrong-signature calls (`E0061`)
   - trait/type mismatch patterns (`E0277`, `E0308`)

4. Add a “tool-call churn” metric to analysis.
   - This run consumed significant effort in prompt/tool interaction after the easy successes.

## Submission Audit

### Novelty Audit

- strengthened slightly
- we now have evidence that different Rust projects fail for different systems reasons

### Methodology Audit

- strengthened
- shows the value of separating:
  - compatibility normalization
  - compile-failure repair/absorption

### Evaluation Audit

- still incomplete
- this is partial evidence only

### Writing Audit

- very important narrative update:
  - do not generalize the `strsim-rs` fix into a universal Rust success claim
  - position it as removal of one important gate, followed by harder remaining failure modes on richer Rust codebases
