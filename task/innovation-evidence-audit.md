# Innovation Evidence Audit

Date: 2026-03-26

## Core Judgment

The current experiments are **not yet sufficient** to fully defend the paper's innovation stack end to end.

They are sufficient to support:

- that the project is no longer just a prototype idea
- that the recovery loop is a real systems mechanism
- that different languages expose different dominant failure layers

They are **not yet sufficient** to support:

- stable cross-language effectiveness
- a strong headline claim that bounded repair already improves outcomes across languages
- a broad comparative claim over simple baselines

But the project now does have a **small baseline sanity set**, so the last gap is no longer completely open.

## Innovation Point Status

### I1. Failure-Layer-Aware Recovery Loop

Status:

- **Partially supported**

Facts:

- Python provides real positive slice-level evidence that deterministic repair can move failures toward successful outcomes.
- Go `DebugFlags` has now moved from pure `llm` retries to repeated `tool_repair+llm` retries:
  - `v8`: `/tmp/cobra-debugflags-v8.jsonl`
  - `v9`: `/tmp/cobra-debugflags-v9.jsonl`
  - `v10` first attempt also entered `tool_repair+llm`:
    - `/tmp/cobra-debugflags-v10.jsonl`

Reasonable inference:

- the recovery loop is real and active, not rhetorical

What is still missing:

- aggregated evidence that the loop improves terminal outcomes on more than isolated slices
- one additional nontrivial paired contrast beyond the current Rust prompt-first pair

### I2. Unified Diagnosis/Repair Interface

Status:

- **Supported at the systems-design level**
- **Partially supported at the empirical level**

Facts:

- The same `DiagnosticIR -> repair -> retry` pattern is used across languages in code.
- Python and Go both now have nontrivial language-specific operators under the same orchestration structure.

Reasonable inference:

- the multi-language story is defensible as a shared control plane with language-specific operators beneath it

What is still missing:

- stronger empirical evidence that this abstraction yields measurable benefits across at least two languages
- one additional paired comparison showing that the shared control plane beats a simpler variant on another nontrivial slice

### I3. Bounded Tool-First Fixpoint Before LLM Retry

Status:

- **Strong on Python**
- **Medium on Go**
- **Weak on Rust**

Facts:

- Python already provides the clearest evidence that bounded repair is useful.
- Go now provides evidence that fixpoint repair is actually being exercised before the next LLM retry.
- Go `DebugFlags` now also has one real positive slice-level result where a repair pass succeeded before the LLM error prompt:
  - `/tmp/cobra-debugflags-v11.jsonl`
  - `/tmp/cobra-debugflags-v11.log`
- Go `ResetFlags` has now recovered again as a second positive slice:
  - `/tmp/cobra-resetflags-v6.jsonl`
  - `/tmp/cobra-resetflags-v6.log`
  - but this one is still prompt-first rather than repair-assisted
- A small baseline sanity set now exists:
  - Python `click`:
    - full:
      - `/tmp/click-full-python-seg-v18.jsonl`
    - baseline:
      - `/tmp/click-baseline-seg-v2.jsonl`
    - contrast:
      - full is repair-assisted positive
      - baseline is llm-only negative
  - Go `DebugFlags`:
    - full:
      - `/tmp/cobra-debugflags-v11.jsonl`
    - baseline:
      - `/tmp/cobra-debugflags-baseline-v1.jsonl`
    - contrast:
      - full is repair-assisted positive
      - baseline is llm-only negative
  - Go `ResetFlags`:
    - full:
      - `/tmp/cobra-resetflags-v6.jsonl`
    - baseline:
      - `/tmp/cobra-resetflags-baseline-v1.jsonl`
    - contrast:
      - both are prompt-first positive
      - so this slice does not need the full loop
  - Go `InitDefaultHelpCmd`:
    - full:
      - `/tmp/cobra-inithelp-v5.jsonl`
    - baseline:
      - `/tmp/cobra-inithelp-baseline-v1.jsonl`
    - contrast:
      - full is repair-engaged negative
      - baseline is llm-only negative
      - so the harder behavior-semantics slice already shows a mechanism difference even without outcome lift
  - Rust `utils.rs:150-191`:
    - full:
      - `/tmp/coverup-target-utils-noproxy.jsonl`
    - baseline:
      - `/tmp/rust-utils-baseline-v2.jsonl`
    - contrast:
      - full is prompt-first positive
      - baseline is llm-only negative
      - so the hardest language now also has a paired baseline contrast, even though the gain is not repair-assisted
- The Go path also exposed a real executability gate:
  - post-repair tests can exceed backend size limits
  - lightweight size-aware compaction in `src/coverup/languages/go_backend.py` is therefore part of the practical bounded-repair story, not just incidental cleanup.

Reasonable inference:

- bounded fixpoint is one of the most defensible method contributions
- but the paper should explicitly separate:
  - slices where the full loop is necessary
  - slices where simpler prompting is already enough

What is still missing:

- replication beyond the current two positive Go slices
- small aggregated evidence showing that repair-assisted benefit on Go is not a one-off path tied only to `DebugFlags`

### I4. Cross-Language Failure-Layer Study

Status:

- **Mostly supported**

Facts:

- Python failures are currently concentrated more in call-shape / oracle / framework API families.
- Go failures concentrate in behavioral preconditions and formatted-output oracle brittleness.
- A newer medium Go slice, `InitDefaultHelpCmd`, sharpens that picture further:
  - `/tmp/cobra-inithelp-v1.jsonl`
  - `/tmp/cobra-inithelp-v3.jsonl`
  - `/tmp/cobra-inithelp-v4.jsonl`
  - `/tmp/cobra-inithelp-v5.jsonl`
  - `/tmp/cobra-inithelp-v6.jsonl`
  - `/tmp/cobra-inithelp-v7.jsonl`
  - `/tmp/cobra-inithelp-v8.jsonl`
  - the failure progression moved from illegal `CheckErr` monkeypatching
  - to wrong temp-module subprocess construction
  - to wrong exit/stderr assumptions
  - to narrower output-format/oracle mismatches
  - and finally to source-level `Find(args)` / `Args`-validator semantics plus helper-process exit/output assumptions
- Rust still remains the hardest language overall, but there is now at least one targeted prompt-first positive slice:
  - `/tmp/coverup-target-utils-noproxy.jsonl`
  - observed path:
    - `llm/F -> llm/G`
  - this is useful as a language-contrast point, not as evidence that Rust repair is mature
- Rust remains hardest and exposes import / type / ownership / semantic-layer failures more strongly.

Reasonable inference:

- this is currently the best-supported multi-language claim

What is still missing:

- broader slice coverage and aggregated trace statistics
- one slice that turns the new exit-path / writer-channel semantic family into a positive recovery case

## What We Can Safely Claim Now

1. We built a coverage-guided recovery loop that diagnoses failed attempts and routes them through structured repair actions before retry.

2. The same orchestration pattern can engage across multiple languages, even though the dominant failure layer differs by language.

3. The same orchestration pattern now has slice-level positive evidence in more than one language, even though the maturity of the language-specific operators still differs.

4. Cross-language evidence should be reported in terms of recovery class and failure layer, not just final gain.

5. Trace-based evaluation is necessary because coverage alone would miss whether recovery is dormant, prompt-only, or repair-assisted.

6. A small targeted baseline sanity set already shows that some slice-level gains really do require the full recovery loop, while others remain prompt-first.

7. On a harder Go behavior-semantics slice, the full loop already changes the recovery class from llm-only failure to repair-engaged failure, and later reruns show that the failure frontier can be pushed from shallow output-format mistakes into source-level command/help semantics even without outcome lift.

8. The baseline sanity story now spans Python, Go, and Rust, rather than stopping at the easier language pairs.

## What We Cannot Safely Claim Yet

1. The method already delivers stable cross-language outcome gains.

2. Go bounded repair is already effective in the same way Python bounded repair is.

3. The full innovation stack has already been experimentally validated at submission strength.

4. Rust bounded repair is already competitive with the Python/Go story.

5. The current baseline sanity set is already broad enough to stand in for a full baseline section.

## Most Important Remaining Gaps

1. Need small-slice aggregated trace evidence, not just individual case studies.

2. Need stronger replication beyond the current two Go positives, especially for repair-assisted benefit.

3. Need one Go slice that turns the newer behavioral-semantics family into an actual recovery result.

4. Need one more paired contrast that is neither a simple prompt-first case nor an already-known Go behavior-semantics negative.

## Next Best Step

The most valuable next step is:

**convert the recovery loop itself into the main evaluation object.**

Concretely:

- report trace-derived terminal outcomes and repair-path metrics
- keep Python as the strongest positive case
- keep Go `DebugFlags` as the first positive non-Python case:
  - repair is no longer dormant
  - repair can now produce slice-level benefit
  - but it is not yet a stable replicated win
- keep Go `ResetFlags` as the complementary simpler case:
  - positive again
  - but still prompt-first
- use the new baseline sanity set to distinguish:
  - full-loop-dependent positives
  - prompt-first positives
- keep `InitDefaultHelpCmd` as the harder negative paired case:
  - full loop changes the recovery class
  - but does not yet produce outcome lift
- keep the Rust `utils.rs` pair as the hardest-language sanity contrast:
  - full is prompt-first positive
  - baseline is llm-only negative
- only claim strong cross-language effectiveness after the Go repair-assisted story replicates on at least one additional slice and we add one more nontrivial paired contrast beyond the current sanity set
