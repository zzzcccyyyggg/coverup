# Innovation Construction Memo

Date: 2026-03-25

## Core Judgment

The paper's strongest innovation is **not**:

- "we use agents for test generation"
- "we support multiple languages"
- "we added a planner"

The strongest innovation is:

**a failure-layer-aware recovery loop for coverage-guided LLM test generation, with a unified diagnosis/repair abstraction that can absorb different dominant failure layers across languages.**

This is the current best path because it is the only framing that is:

- supported by real code structure
- increasingly supported by targeted evidence
- broad enough to matter
- narrow enough to defend against simpler baselines

## Project Reconstruction

Current system, in its publishable form, is converging to three layers:

1. Reachability layer
   - coverage segments
   - blocker / reachability hints
   - purpose: tell the model not only *where* coverage is missing, but *why execution is not reaching it*

2. Recovery layer
   - `DiagnosticIR`
   - error classification
   - bounded tool-first repair
   - LLM retry after repair fixpoint
   - purpose: turn failures from black-box retries into structured recovery steps

3. Language adaptation layer
   - small language-specific operators
   - purpose: absorb different failure families without building a separate system per language

## Facts Already Supported

### Python

- Python currently provides the clearest evidence for bounded repair and operator correctness.
- We have real slice-level evidence that deterministic repair can move a run from syntax/executability failure toward assertion-level reasoning and then to `G`.

### Go

- Go now provides real evidence that the recovery layer is no longer dormant on a harder slice.
- On `cobra/DebugFlags`, the system has moved from:
  - plain `llm` retries
  - to `tool_repair+llm` retries with non-empty fix sets
- This is still not an outcome-gain story, but it is already a recovery-loop story.

### Rust

- Rust remains the hardest slice family.
- Rust currently supports the claim that different languages expose different dominant failure layers.
- Rust does **not** currently support the claim that our repair layer is uniformly mature.

## Reasonable Inferences

1. The real novelty is the **control loop**, not any single operator.

2. The cross-language result we should aim to defend is:
   - different languages fail differently
   - but the same orchestration loop can ingest those failures through a common interface

3. The paper is strongest if it claims:
   - "we make retries structured"
   - not:
   - "we discovered one magic prompt"

## Hypotheses Still Needing Validation

1. A bounded repair fixpoint can reduce useless retries and accelerate movement from executability failures to semantic failures.

2. The same recovery abstraction can provide measurable gains in at least two languages, even if the useful operators differ.

3. Trace-derived recovery metrics may become a stronger headline result than raw coverage alone.

## High-Risk Directions

### Direction 1: selling "multi-language" as the main novelty

Risk:

- `ASTER`-style prior work weakens this heavily.
- Reviewer response will be: "supporting multiple languages is engineering unless the system insight is new."

### Direction 2: selling planner/UCB as the main novelty

Risk:

- too easy to undercut
- too easy to replace with a simpler baseline
- not where the current positive evidence is accumulating

### Direction 3: selling benchmark-specific repair rules as contributions

Risk:

- reviewer will call them ad hoc patches
- they only become publishable if we show they instantiate a more general operator abstraction

### Direction 4: claiming cross-language stable effectiveness too early

Risk:

- unsupported today
- Python is ahead of Go; Go is ahead of Rust on some axes; maturity is uneven

## Proposed Innovation Stack

### C1. Failure-Layer-Aware Recovery Loop

Claim:

- LLM test generation should not treat failed attempts as homogeneous retries.
- Instead, failures should be classified into layers and routed through different recovery actions.

Why this matters:

- This is system-level, not benchmark-level.
- It directly addresses a weakness of naive coverage-guided LLM testing.

Evidence status:

- partially supported now
- needs broader trace-level aggregation

### C2. Unified Diagnosis/Repair Interface

Claim:

- `DiagnosticIR + operator interface` provides a language-agnostic control plane while allowing language-specific repairs underneath.

Why this matters:

- This is the piece that makes the multi-language story defensible.
- Without this layer, "multi-language" is just separate prompt engineering.

Evidence status:

- strongly supported by code structure
- moderately supported by Python and Go targeted runs

### C3. Bounded Tool-First Fixpoint Before LLM Retry

Claim:

- a bounded fixpoint of deterministic repairs before another LLM call improves the quality of the retry loop
- even when it does not immediately improve final coverage
- lightweight executability controls, such as size-aware compaction, belong inside this fixpoint rather than outside the method story

Why this matters:

- it is a concrete systems mechanism
- it differentiates us from memoryless retry pipelines
- it explains why some gains come from clearing repair-induced execution gates before another model round

Evidence status:

- strong on Python
- medium on Go and improving after the first positive `DebugFlags` rerun
- weak on Rust

### C4. Cross-Language Failure-Layer Study

Claim:

- the dominant failure layer differs by language:
  - Python: call-shape / oracle / framework API
  - Go: behavioral preconditions / output oracle brittleness
  - Rust: import / type / ownership / semantic slices

Why this matters:

- this converts "multi-language support" into an empirical systems insight

Evidence status:

- increasingly supported
- likely publishable if reported carefully and paired with trace metrics

## Contribution Wording That Is Likely Defensible

Current best draft:

1. We present a coverage-guided LLM test generation loop that explicitly diagnoses failed attempts and routes them through bounded recovery actions rather than naive retry.

2. We introduce a unified diagnosis-and-repair abstraction that separates language-agnostic orchestration from language-specific recovery operators.

3. We show, across Python, Go, and Rust slices, that dominant failure layers differ substantially by language, and that structured recovery can begin to absorb those differences.

## Contribution Wording To Avoid

Avoid:

- "the first multi-language LLM test generator"
- "our planner efficiently explores coverage"
- "our operators improve performance across all languages"
- "our method consistently outperforms baseline across the board"

## Evaluation Design Needed To Support The Innovation

### Must-Have Metrics

- final coverage
- trace-derived terminal `G/F/U`
- number of tool-repair passes
- whether recovery path was `llm` or `tool_repair+llm`
- failure-category transition counts
- cost / attempts

### Must-Have Comparisons

- baseline retry loop
- full recovery loop
- no-blocker
- no-memory
- no-tool-repair-fixpoint

### Strong Supporting Analysis

- failure-layer transition diagrams
- distribution of dominant failure layers per language
- case studies where deterministic repair converts a useless retry into a meaningful retry

## Writing Strategy

Best single-sentence narrative:

**Coverage tells the model where execution is missing, but not why attempts fail; we add a structured recovery loop that diagnoses those failures and applies bounded repairs before retrying, and show that this matters differently across languages.**

Suggested section logic:

1. Problem:
   - naive coverage-guided LLM retries are too coarse
2. Insight:
   - failures have layers, and retries should depend on the layer
3. Method:
   - blocker + `DiagnosticIR` + bounded repair + retry
4. Cross-language finding:
   - languages differ mainly in dominant failure layer, not in the need for recovery
5. Evaluation:
   - trace-based evidence, not coverage alone

## Immediate Next Step

The next most valuable paper-oriented action is:

**turn the recovery loop itself into the evaluation object.**

Concretely:

- aggregate trace-derived recovery metrics on a small Python/Go slice set
- stop relying on coverage alone as the main proof
- use Go `DebugFlags` as the negative/transition case:
  - not yet a success
  - but already a clear proof that the recovery layer can engage across languages
