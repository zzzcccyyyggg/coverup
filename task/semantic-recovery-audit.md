# Semantic Recovery Audit

Date: 2026-03-25

Scope:
- objective: reduce repeated Rust `panic/assertion/unknown` churn after compile gates are mostly removed
- status: code implemented, synthetically verified, and live-validated on a targeted hard segment
- status of real validation: completed for control-flow wiring; not yet completed for benchmark-level effectiveness

## Core Judgment

This step now has live evidence that the *control logic* is wired correctly, but still does not have evidence of stable outcome improvement.

The main value is that we now distinguish two qualitatively different repair phases:

1. compiler-friction repair
2. semantic/oracle recovery after repeated stalled retries

That distinction was missing before, and one real control-flow bug had to be fixed before the semantic branch could even trigger on repeated coverage stalls.

## Facts

Implemented changes:

- `improve_coverage()` now records per-segment retry history and exposes the current `DiagnosticIR` to the prompter [coverup.py](/home/zzzccc/coverup/src/coverup/coverup.py#L529)
- Rust error prompts now enter `Semantic recovery mode` after repeated non-success retries on panic/assertion-like failures [gpt_rust_v1.py](/home/zzzccc/coverup/src/coverup/prompt/gpt_rust_v1.py#L120)
- Rust missing-coverage prompts now also enter `Semantic recovery mode` after repeated non-success retries on panic/assertion-like failures [gpt_rust_v1.py](/home/zzzccc/coverup/src/coverup/prompt/gpt_rust_v1.py#L142)
- Rust dynamic guidance now includes range/slice semantics guidance for range-remapping code [gpt_rust_v1.py](/home/zzzccc/coverup/src/coverup/prompt/gpt_rust_v1.py#L350)
- Rust memory fallback templates now include `panic` and `unknown` categories, so semantic guidance can be injected even without prior successful recipes [memory.py](/home/zzzccc/coverup/src/coverup/agents/memory.py#L141)

Verification completed:

- `.venv/bin/python -m py_compile src/coverup/coverup.py src/coverup/prompt/gpt_rust_v1.py src/coverup/agents/memory.py`
- synthetic prompt check confirmed that repeated-failure context emits a `Semantic recovery mode` section with semantic-debugging guidance

Real-run validation completed:

- targeted `similar/src/utils.rs:150-191` rerun initially failed only because the local proxy broke DeepSeek connectivity; direct no-proxy access worked
- after bypassing the proxy, the same targeted `utils` rerun succeeded end-to-end with `1 F -> 1 G` and `81.0% -> 83.4%` coverage, proving live model execution was available
- targeted `similar/src/algorithms/compact.rs:248-350` rerun then exposed a real control-flow gap: repeated `U` outcomes never saw `Semantic recovery mode` because `missing_coverage_prompt()` did not include it
- after patching that gap, a repeated-stall live rerun on the same `compact` segment produced `F=1, U=2, G=0` and the third live prompt explicitly contained:
  - `Semantic recovery mode:`
  - `This segment has stalled for 2 recent attempt(s) without a new G`
- relevant artifacts:
  - [coverup-target-compact-semantic.jsonl](/tmp/coverup-target-compact-semantic.jsonl)
  - [coverup-target-compact-semantic.log](/tmp/coverup-target-compact-semantic.log)
- therefore the branch is now live-validated as *reachable and wired correctly*

## Strong Inferences

- The system now has an explicit mechanism for transitioning from “fix compile problems” to “reconstruct semantics”.
- This directly addresses the failure pattern seen in `similar`, where later retries were dominated by semantic/panic mismatch rather than early import errors.
- The previous absence of live semantic-mode evidence was not purely because hard segments were too difficult; it was partly caused by a control-flow omission on the repeated-coverage-stall path.

## Hypotheses Needing Validation

- Hypothesis: the new recovery mode reduces repeated panic/coverage-stall churn on hard Rust segments like `src/algorithms/compact.rs:248-350`.
- Hypothesis: adding `panic`/`unknown` fallback templates helps before reflective memory has enough data to inject lessons.
- Hypothesis: the semantic mode is more valuable on repeated `U` and mixed `F/U` traces than on straightforward compile-error traces, because easy compile failures already recover without it.

## High-Risk or Unsupported Claims

- Unsupported: “semantic recovery improves coverage on `similar` overall.”
- Unsupported: “the new retry mode is benchmark-robust.”
- High risk: turning branch reachability evidence into performance evidence.
- High risk: citing the successful `utils` targeted run as semantic-recovery evidence; it succeeded before the semantic branch was needed.

## Most Valuable Next Step

The next high-value step is no longer “prove the branch executes.” That is done.

The next step is to test whether the branch *helps*:

1. run paired targeted reruns on the same hard segment with semantic mode enabled vs disabled
2. compare repeated-stall length, final `G/F/U`, and whether the model converges to smaller invariant-based tests

Only that comparison will make this mechanism paper-usable as more than a wiring fix.
