# Paper Outline v2

> Working title: **Failure-Layer-Aware Recovery for Coverage-Guided LLM Test Generation**
>
> Positioning: software engineering / testing systems paper
>
> Status: aligned with current evidence as of 2026-03-26

## 0. One-Sentence Thesis

Coverage tells the model where execution is missing, but not why attempts fail; we add a structured recovery loop that diagnoses failed attempts and applies bounded repairs before retrying, and show that this matters differently across Python, Go, and Rust.

## 1. Abstract Skeleton

1. Problem:
   - coverage-guided LLM test generation often degenerates into coarse retry loops
   - missing coverage alone does not explain why attempts fail

2. Insight:
   - failures have layers
   - retries should depend on the diagnosed failure layer rather than treating every failed attempt the same way

3. Method:
   - coverage-guided orchestration
   - `DiagnosticIR`
   - bounded tool-first fixpoint before another LLM retry
   - language-specific operators under one recovery loop

4. Evidence:
   - trace-based evaluation
   - repair-assisted positive slices in more than one language family
   - prompt-first positives and harder negatives reveal different recovery classes

5. Claim boundary:
   - the paper is about structured recovery behavior, not stable benchmark-wide dominance

## 2. Introduction

### 2.1 Problem Setup

- LLM test generation can identify missing targets but still fail repeatedly for different reasons:
  - executability failures
  - API-shape failures
  - public-surface misuse
  - brittle output or oracle mismatches
  - language-specific semantic mistakes

### 2.2 Gap in Existing Framing

- coverage alone is not enough as the system feedback signal
- current systems are often evaluated mainly on final coverage, which obscures whether retries are:
  - dormant
  - prompt-only
  - repair-engaged
  - repair-assisted

### 2.3 Main Insight

- failed attempts should be routed through different recovery actions depending on failure layer

### 2.4 Contributions

1. A failure-layer-aware recovery loop for coverage-guided LLM test generation.
2. A unified diagnosis-and-repair abstraction (`DiagnosticIR + operator interface`) that separates orchestration from language-specific recovery.
3. A bounded tool-first fixpoint that turns some retries from blind generation into structured recovery.
4. A cross-language finding that dominant failure layers differ by language, so multi-language support should be reported as a failure-layer study under one control loop.

## 3. Motivating Examples

Use two examples, not one.

### 3.1 Positive Example

- Python `click` or Go `DebugFlags`
- show:
  - naive attempt fails
  - deterministic repair changes the retry
  - next attempt becomes `G`

### 3.2 Harder Negative Example

- Go `InitDefaultHelpCmd`
- show:
  - full loop changes the recovery class
  - but the slice remains negative
  - the failure frontier still moves from shallow formatting mistakes into deeper command/help semantics

Purpose:

- establish that the method contribution is not "we always win"
- it is "we change how retries behave, and sometimes that produces outcome lift"

## 4. Method

### 4.1 System Overview

Pipeline:

1. select coverage segment
2. derive reachability hint / blocker context
3. generate candidate test
4. execute + measure
5. classify failure into `DiagnosticIR`
6. run bounded tool-first repair fixpoint
7. retry with updated context if needed

### 4.2 Failure-Layer-Aware Recovery

Define the core object:

- an attempt is not just success/failure
- it belongs to a failure layer that determines the next action

Suggested language:

- executability
- visibility/public-surface
- call-shape/signature
- assertion/oracle
- semantic/behavioral

### 4.3 Unified Diagnosis/Repair Interface

Explain:

- why `DiagnosticIR` matters
- why operators should live below a common control plane
- why this is what makes the multi-language story defensible

### 4.4 Bounded Tool-First Fixpoint

Explain:

- deterministic repair passes happen before another LLM round
- why boundedness matters
- why executability controls can be treated as part of repair rather than external engineering glue

### 4.5 Language-Specific Operators

Keep this section small and honest.

- Python:
  - call-shape normalization
  - oracle/output repair
- Go:
  - public-surface and output-oracle repair
  - helper-process / behavior-semantic guidance
- Rust:
  - import / type / ownership / hard semantic slices

Important boundary:

- the operators are not the main novelty
- they instantiate the recovery abstraction

## 5. Evaluation Setup

### 5.1 Evaluation Philosophy

State explicitly:

- the main evaluation object is the recovery loop
- therefore trace-derived metrics are first-class

### 5.2 Metrics

Must include:

- final coverage
- terminal `G/F/U`
- observed recovery class
- repair-engaged attempts
- average repair passes
- fixpoint exhaustion

### 5.3 Comparisons

At minimum:

- baseline retry loop
- full recovery loop

Strong additions if available:

- `no-tool-repair-fixpoint`
- `no-blocker`
- `no-memory`

### 5.4 Slice Set

Do not oversell benchmark breadth.

Use:

- a small targeted slice set across Python / Go / Rust
- frame this as mechanism evidence plus baseline sanity, not benchmark-wide dominance

## 6. Results

### 6.1 Mechanism Table First

Use the table generated from:

- [paper_trace_tables.py](/home/zzzccc/coverup/experiments/scripts/paper_trace_tables.py)

Headline:

- repair-assisted positives exist
- prompt-first positives exist
- repair-engaged negatives exist

### 6.2 Paired Baseline Sanity

Headline:

- some gains are full-loop-dependent
- some slices are prompt-first even under baseline
- harder negative pairs still provide mechanism evidence

### 6.3 Cross-Language Failure Layers

Frame the cross-language result as:

- Python concentrates more in call-shape / oracle / framework API families
- Go concentrates more in behavioral preconditions and output semantics
- Rust remains the hardest and concentrates more in import / type / ownership / semantic layers

### 6.4 Case Studies

One positive, one harder negative.

## 7. Discussion

### 7.1 What the Paper Is Actually About

- not "we support three languages"
- not "we invented a planner"
- not "we dominate all baselines"
- instead:
  - we make retries structured
  - we expose recovery classes
  - we show that the same loop behaves differently across languages

### 7.2 Threats / Limitations

- targeted slice evidence is still small
- language maturity is uneven
- some strongest evidence is mechanism-level rather than large-scale effectiveness
- Rust repair is not yet mature

## 8. What To Avoid Writing

Avoid these contribution framings:

1. "the first multi-language LLM test generator"
2. "our planner is the key innovation"
3. "our operators consistently improve all languages"
4. "we already have stable cross-language outcome gains"

## 9. Figures and Tables

### Table 1

- mechanism table
- recovery class / observed path / repair engagement

### Table 2

- paired baseline sanity table

### Figure 1

- failure-layer-aware recovery loop diagram

### Figure 2

- cross-language failure-layer map
  - Python
  - Go
  - Rust

### Figure 3

- one positive case-study timeline
  - naive failure
  - repair
  - positive retry

### Figure 4

- one harder negative timeline
  - baseline
  - full-loop reruns
  - frontier movement without final `G`

## 10. Immediate Writing Order

Write in this order:

1. Introduction
2. Method overview
3. Mechanism table section
4. Baseline sanity section
5. Cross-language finding section
6. Threats / limitations
7. Abstract

This order forces the paper to stay aligned with current evidence rather than drifting back to stale blocker/memory/planner storytelling.
