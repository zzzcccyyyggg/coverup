# `similar` Structured-Hint Rerun Audit

Date: 2026-03-25

Scope:
- project: `similar`
- seed: `42`
- variant: patched `full`
- output root: `/tmp/coveragent-similar-full-v2`
- workspace: `/tmp/coveragent-similar-workspace`
- run status: manually interrupted after the failure mode stabilized

Important limitation:
- This was a real model-driven rerun, but it was manually stopped before a final result JSON was written.
- It is valid as partial evidence about failure composition and prompt behavior.
- It is **not** valid as a completed coverage result.

## Core Judgment

This rerun supports a narrower, more precise claim than the earlier `similar` partial run:

- the new Rust prompt/backend changes appear to reduce early compile-gate failures,
- but they do **not** yet convert `similar` into a healthy closed-loop run,
- because the dominant bottleneck quickly shifts from compile gating to semantic/panic-heavy debugging on a small set of hard segments.

So the latest evidence says:

1. the new changes improved the *shape* of failure,
2. but they did not yet improve the *closure* of the loop.

## Code Changes Under Test

This rerun evaluated three concrete prompt/diagnostic changes:

- structured cargo-derived fix hints are now appended to Rust error prompts and propagated into `DiagnosticIR` [rust_backend.py](/home/zzzccc/coverup/src/coverup/languages/rust_backend.py#L405)
- Rust dynamic guidance now explicitly warns about lifetime-temporary borrowing, explicit `Algorithm` parameters, and `Index<usize>`-style APIs [gpt_rust_v1.py](/home/zzzccc/coverup/src/coverup/prompt/gpt_rust_v1.py#L333)
- Rust memory templates now push more literal use of compiler labels for type/ownership failures [memory.py](/home/zzzccc/coverup/src/coverup/agents/memory.py#L141)

Static verification passed before the rerun:

- `.venv/bin/python -m py_compile src/coverup/languages/rust_backend.py src/coverup/prompt/gpt_rust_v1.py src/coverup/agents/memory.py`

## Facts Supported by the New Partial Trace

From `/tmp/coveragent-similar-full-v2/traces/similar_full_s42.jsonl` at interruption time:

- total attempts observed: `21`
- outcomes: `1 G / 17 F / 3 U`
- segments attempted: `5`
- segments good: `1`
- segments failed: `4`
- segments useless: `1`

Diagnostic composition:

- `panic`: `14`
- `unknown`: `4`
- `type`: `2`
- `visibility`: `1`

Observed error codes:

- `E0061 x1`
- `E0277 x1`
- `E0616 x1`

Prompt/runtime behavior:

- memory injected attempts: `0`
- blocker injected attempts: `21`
- tool repair attempts: `0`
- tool repair full successes: `0`

Observed successful segment:

- `src/types.rs:340-377`

Observed failing segments:

- `src/algorithms/compact.rs:146-245`
- `src/algorithms/compact.rs:248-350`
- `src/types.rs:409-458`
- `src/utils.rs:150-191`

Log evidence that the new signal path was active:

- `STRUCTURED FIX HINTS:` appeared in the live error prompt
- the model explicitly queried `ChangeTag`, `TextDiff`, and `diff_slices` while debugging `src/utils.rs:150-191`
- the dominant `utils.rs:150-191` failures became assertion/panic-style semantic mismatches about `TextDiffRemapper` slice semantics, not early import/visibility crashes

## Comparison Against the Earlier `similar` Partial Run

Earlier partial run summary from [similar-partial-smoke-audit.md](/home/zzzccc/coverup/task/similar-partial-smoke-audit.md):

- `38` attempts
- `4 G / 28 F / 6 U`
- `10` segments attempted
- dominant codes included `E0603`, `E0624`, `E0061`, `E0277`, `E0716`, `E0308`
- memory and tool repair both participated

Current rerun summary:

- `21` attempts
- `1 G / 17 F / 3 U`
- `5` segments attempted
- early explicit codes are much narrower: `E0061`, `E0277`, `E0616`
- memory and tool repair did not participate at all

What this comparison does support:

- the new changes likely suppressed some early compile-gate patterns that were prominent before
- the run now collapses faster into semantic/panic debugging on a few segments

What this comparison does **not** support:

- any claim that the new patch is globally better on `similar`
- any claim that coverage would have ended higher or lower without a completed run
- any ranking against `no_planner` / `no_blocker`

The stopping times are different, so absolute totals must be interpreted cautiously.

## Strong Inferences

- The structured-hint path is working mechanically; this is directly supported by the log.
- The prompt/backend changes seem to have moved failure mass away from the earlier import/visibility/ownership gate cluster.
- The new dominant problem on `similar` is semantic understanding and oracle construction for a small number of hard Rust segments, especially `src/utils.rs:150-191`.
- The current agent stack still lacks an effective mechanism for escaping repeated panic/semantic retries once compile errors are mostly gone.

## Hypotheses Needing Further Validation

- Hypothesis: structured fix hints help with *compile* absorption but not with *semantic* recovery.
- Hypothesis: once compile gates are lowered, the next limiting factor is not repair but example/semantics guidance for APIs like `TextDiffRemapper`.
- Hypothesis: the current memory cold-start behavior is too conservative for short hard slices, so the rerun never accumulates enough success signal to change later prompts.

These are plausible, but still require a controlled follow-up experiment.

## High-Risk or Unsupported Directions

- High risk: claiming the new patch “improves Rust performance” based on this rerun.
- High risk: claiming blocker/planner are the key issue on `similar` from this evidence alone.
- Unsupported: saying repair no longer matters on `similar`; this rerun only shows that repair did not activate in this specific partial execution.

## Most Valuable Next Steps

1. Add semantic/oracle guidance for `panic`-heavy Rust segments.
   - The best current target is `src/utils.rs:150-191`.
   - The repeated failures there are about understanding `TextDiffRemapper` slice semantics, not about compiling.

2. Add a second-layer error prompt for repeated panic/assertion failures.
   - After 2-3 failed retries on the same segment, the prompt should switch from “fix compile issues” to “infer the exact runtime semantics from the implementation and existing tests”.

3. Revisit memory cold-start for short hard runs.
   - With only one observed `G`, the current rerun never injected memory.
   - We need to decide whether this is desirable conservatism or harmful under-learning.

4. Keep the paper story narrow.
   - For now, the strongest supported claim is not “better Rust overall”.
   - It is “structured compile guidance changes the failure frontier, but semantic closure remains open.”

## Submission Audit

### Novelty Audit

- mildly strengthened
- we now have stronger evidence that “agentic test generation” should be decomposed into at least two layers:
  - compile-gate absorption
  - semantic/oracle closure

### Methodology Audit

- strengthened
- this rerun validates that backend/prompt changes can measurably change failure composition, even when final coverage is not yet better

### Evaluation Audit

- still incomplete
- this remains partial evidence only
- no final coverage number or completed cost/benefit statement can be made

### Writing Audit

- the writing should explicitly distinguish:
  - fixes that reduce compiler-friction
  - fixes that improve semantic understanding
- current evidence only supports the first category
