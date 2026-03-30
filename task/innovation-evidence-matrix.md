# Innovation Evidence Matrix

Date: 2026-03-25

## Core Judgment

The paper's strongest innovation is **not**:

- multi-language support by itself
- agent use by itself
- the planner by itself

The strongest innovation is:

- a **failure-layer-aware recovery loop**
- implemented as `reachability hint -> diagnosis -> bounded tool-first repair -> retry`
- with a language-agnostic control plane and language-specific operators

This matrix maps each intended paper claim to the current evidence, risk, and the next experiment needed to make the claim publishable.

## Claim Matrix

### C1. Failure-Layer-Aware Recovery Loop

Claim:

- failed attempts should not be treated as homogeneous retries
- the system should route different failure layers through different recovery actions

Current supporting evidence:

- Python targeted evidence:
  - `click` slice shows deterministic repair can move execution from syntax/executability failure toward assertion-level reasoning and then to `G`
  - see:
    - `task/python-click-recovery-audit.md`
- Go targeted evidence:
  - `DebugFlags` moved from:
    - prompt-only failure
    - to `tool_repair+llm` activity
    - to a positive repair-assisted `G`
  - `ResetFlags` also now has a renewed positive run under the current stack, though via a prompt-first path
  - see:
    - `/tmp/cobra-debugflags-v8.jsonl`
    - `/tmp/cobra-debugflags-v9.jsonl`
    - `/tmp/cobra-debugflags-v11.jsonl`
    - `/tmp/cobra-resetflags-v6.jsonl`
    - `task/cross-language-smoke-audit.md`

What is directly supported:

- the loop is real
- the loop is not dormant across languages
- routing by failure layer changes behavior and sometimes outcome

What is still not supported:

- stable effectiveness across multiple slices per language

Current status:

- **Supported as a systems mechanism**
- **Partially supported as an effectiveness claim**

Main reviewer risk:

- "this is still a collection of case studies, not a stable experimental pattern"

Next evidence needed:

- trace-based aggregation over a small slice set

### C2. Unified Diagnosis/Repair Interface

Claim:

- `DiagnosticIR + operator interface` gives one control plane for multiple languages

Current supporting evidence:

- same orchestration in code across Python / Go / Rust
- language-specific operators plugged under the same loop
- concrete code paths:
  - `src/coverup/coverup.py`
  - `src/coverup/agents/repair.py`
  - `src/coverup/diagnostic_ir.py`

What is directly supported:

- this abstraction exists in the implementation
- it is not just prompt branching

What is still not supported:

- strong empirical proof that the abstraction itself is the cause of gains

Current status:

- **Strongly supported at design level**
- **Moderately supported empirically**

Main reviewer risk:

- "this is good software architecture, but why is it a research contribution?"

Next evidence needed:

- show at least two languages with positive or near-positive recovery traces under the same evaluation protocol

### C3. Bounded Tool-First Fixpoint Before LLM Retry

Claim:

- deterministic tool-side repairs before another LLM round improve the retry loop
- lightweight executability controls belong inside this fixpoint

Current supporting evidence:

- Python:
  - strongest evidence that bounded repair and operator correctness change outcomes
  - see `task/python-click-recovery-audit.md`
- Go:
  - `DebugFlags v11` now shows:
    - `tool_repair+llm`
    - `repair_passes=1`
    - direct `G`
    - skipped LLM error prompt after successful repair
  - `ResetFlags v4/v5` show that invalid `FlagSet` accessor failures are a family rather than a single bug
  - `ResetFlags v6` shows the simpler slice can recover positively again after that family is better understood
  - size-limit failure in `v10` exposed executability as part of the repair story
  - Go backend now includes size-aware compaction:
    - `src/coverup/languages/go_backend.py`

What is directly supported:

- bounded repair is not just being called; it can produce successful outcomes
- executability gates can be part of the recovery story

What is still not supported:

- stable repair-assisted positive evidence on more than one non-Python slice

Current status:

- **Strong on Python**
- **Medium and improving on Go**
- **Weak on Rust**

Main reviewer risk:

- "repair helped once, but is it mature or robust?"

Next evidence needed:

- one more positive or near-positive Go slice using the same trace-based evaluation

### C4. Cross-Language Failure-Layer Study

Claim:

- different languages expose different dominant failure layers

Current supporting evidence:

- Python:
  - call-shape / oracle / framework API
- Go:
  - behavioral preconditions / output oracle brittleness / executability gate
- Rust:
  - import / type / ownership / semantic hard slices
- see:
  - `task/cross-language-smoke-audit.md`
  - `task/strsim-smoke-audit.md`
  - `task/similar-rerun-audit.md`

What is directly supported:

- this is currently the best-supported multi-language claim

What is still not supported:

- broad benchmark-level generalization

Current status:

- **Mostly supported**

Main reviewer risk:

- "the language-study evidence is too narrow in benchmark coverage"

Next evidence needed:

- a small per-language slice set with the same trace-derived metrics

## What We Can Safely Claim Now

1. We built a coverage-guided recovery loop that diagnoses failed attempts and routes them through structured repair actions before retrying.

2. The same orchestration pattern can engage across multiple languages, even though the dominant failure layer differs by language.

3. Bounded repair is one of the most defensible method contributions, especially when evaluated via trace-derived outcomes rather than raw coverage alone.

4. Multi-language is best defended as a **failure-layer study under one control loop**, not as raw language-count novelty.

## What We Still Cannot Safely Claim

1. Stable cross-language effectiveness.

2. Go repair maturity comparable to Python.

3. Submission-strength end-to-end validation of the full innovation stack.

## Highest-Value Next Experiments

1. Replicate the new positive Go result on one additional slice.

2. Build a small trace-based aggregation table:
   - terminal `G/F/U`
   - repair-assisted vs prompt-only
   - average repair passes
   - fixpoint exhaustion

3. Keep Rust in the paper, but use it as the hard-language evidence, not the sole representative of system difficulty.
