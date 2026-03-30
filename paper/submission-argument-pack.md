# Submission Argument Pack

Date: 2026-03-26

## Core Judgment

The paper is now strongest when framed as a **systems/software-engineering paper about structured recovery**, not as:

- a generic "agent for test generation" paper
- a generic "multi-language support" paper
- a planner/UCB paper

The most defensible thesis is:

**Coverage tells the model where execution is missing, but not why attempts fail; we add a failure-layer-aware recovery loop that diagnoses failed attempts and routes them through bounded repairs before retry, and show that this changes recovery behavior differently across languages.**

## Project Reconstruction

The current publishable system has converged to three layers:

1. Reachability layer
   - coverage segments
   - blocker / reachability hints
   - role: move the prompt from "where coverage is missing" toward "why execution is not reaching it"

2. Recovery layer
   - `DiagnosticIR`
   - failure categorization
   - bounded tool-first fixpoint
   - LLM retry after repair exhaustion
   - role: turn naive retries into structured recovery

3. Language-adaptation layer
   - small language-specific operators
   - role: absorb different dominant failure families without building three unrelated systems

## Current Best Contribution Stack

### C1. Failure-Layer-Aware Recovery Loop

Claim:

- failed attempts should not be treated as homogeneous retries
- retries should depend on failure layer

Safe wording:

- we present a coverage-guided recovery loop that explicitly diagnoses failed attempts and routes them through bounded recovery actions before retry

### C2. Unified Diagnosis/Repair Interface

Claim:

- `DiagnosticIR + operator interface` separates language-agnostic orchestration from language-specific recovery

Safe wording:

- we introduce a unified diagnosis-and-repair abstraction that lets one control loop operate across multiple languages while keeping the actual repair operators language specific

### C3. Bounded Tool-First Fixpoint

Claim:

- deterministic repair passes before another LLM round improve the retry loop
- lightweight executability controls belong inside the fixpoint story

Safe wording:

- bounded tool-first repair is one of the main system mechanisms that distinguishes the approach from memoryless retry pipelines

### C4. Cross-Language Failure-Layer Study

Claim:

- different languages expose different dominant failure layers

Safe wording:

- the same orchestration pattern engages across Python, Go, and Rust, but the dominant failure layer differs substantially by language

## Paper-Facing Mechanism Table

Generated from:

- [paper_trace_tables.py](/home/zzzccc/coverup/experiments/scripts/paper_trace_tables.py)

| Slice | Recovery Class | Observed Path | Last Cat | RepairEng | AvgPass | Representative Fixes | Paper Role |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| Python / click / version_option | repair-assisted positive | tool_repair+llm/F -> tool_repair+llm/G | unknown | 2 | 1.50 | python_reorder_version_option_args, python_fix_click_version_option_oracles, python_fix_click_echo_patch_target | repair-assisted positive |
| Python / click / failed variant | repair-engaged negative | tool_repair+llm/F x3 | syntax | 3 | 2.00 | python_reorder_version_option_args, python_fix_click_version_option_oracles | repair-engaged negative |
| Go / cobra / DebugFlags | repair-assisted positive | tool_repair+llm/G | unknown | 1 | 1.00 | go_add_nonempty_output_helper, go_add_line_normalizer, go_add_normalized_contains_helper | repair-assisted positive |
| Go / cobra / ResetFlags | prompt-first positive | llm/G | unknown | 0 | 0.00 | - | prompt-first positive |
| Go / cobra / InitDefaultHelpCmd | repair-engaged negative | tool_repair+llm/F x2 | assertion | 2 | 0.50 | go_mark_unused_binding(exitCode), go_mark_unused_binding(exitOutput) | repair-engaged negative |
| Rust / similar / TextDiffRemapper | prompt-first positive | llm/F -> llm/G | unknown | 0 | 0.00 | - | prompt-first positive |

Interpretation:

- repair-assisted positives exist in more than one language family
- prompt-first positives also exist in more than one language family
- repair-engaged negatives remain visible in both Python and Go
- therefore the correct evaluation object is the **recovery path**, not just final coverage

## Paired Baseline Sanity Table

| Slice | Full Path | Full Class | Baseline Path | Baseline Class | Claim Boundary |
| --- | --- | --- | --- | --- | --- |
| Python / click / version_option | tool_repair+llm/F -> tool_repair+llm/G | repair-assisted positive | llm/F x3 | llm-only negative | full-loop-dependent positive |
| Go / cobra / DebugFlags | tool_repair+llm/G | repair-assisted positive | llm/F x2 | llm-only negative | full-loop-dependent positive |
| Go / cobra / ResetFlags | llm/G | prompt-first positive | llm/F -> llm/G | prompt-first positive | prompt-first or easier positive |
| Go / cobra / InitDefaultHelpCmd | tool_repair+llm/F | repair-engaged negative | llm/F x2 | llm-only negative | harder negative paired contrast |
| Rust / similar / TextDiffRemapper | llm/F -> llm/G | prompt-first positive | llm/F x2 | llm-only negative | mixed paired contrast |

Interpretation:

- some slice-level wins genuinely require the full loop
- some slices are simpler and remain prompt-first even under baseline
- harder negative pairs are still useful because they show mechanism differences without claiming effectiveness

## What We Can Safely Claim Now

1. We built a coverage-guided recovery loop that diagnoses failed attempts and routes them through structured repair actions before retry.
2. The same orchestration pattern engages across multiple languages, even though dominant failure layers differ by language.
3. Bounded repair is a real system mechanism, not just dead code or post-hoc patching.
4. Trace-based evaluation is necessary because coverage alone hides whether recovery is dormant, prompt-first, repair-engaged, or repair-assisted.
5. A small baseline sanity set already shows that some targeted gains depend on the full loop rather than a simple retry baseline.
6. Harder negative slices are informative because they reveal deeper semantic families and sharpen contribution boundaries.

## What We Cannot Safely Claim Yet

1. Stable cross-language effectiveness.
2. Go repair maturity comparable to Python.
3. Rust repair maturity comparable to Python or Go.
4. Submission-strength validation of the entire innovation stack.
5. That the current targeted baseline set is broad enough to replace a full baseline section.

## Writing Strategy

The paper should foreground the following single-sentence narrative:

**Coverage tells us where execution is missing; structured recovery tells us why attempts fail and how to react before retrying.**

Recommended section logic:

1. Introduction
   - naive coverage-guided retries are too coarse
   - the real bottleneck is failure handling, not just target selection

2. Motivating examples
   - one repair-assisted positive slice
   - one harder negative slice
   - show why both are needed

3. Method
   - reachability hint
   - `DiagnosticIR`
   - bounded tool-first fixpoint
   - language-specific operators under one control plane

4. Evaluation protocol
   - trace-derived terminal outcomes
   - recovery classes
   - baseline sanity contrasts

5. Results
   - mechanism table first
   - paired baseline table second
   - raw coverage as supporting evidence, not the only headline

6. Discussion / threats
   - uneven language maturity
   - targeted slices vs benchmark-scale generalization
   - harder negative families are evidence of scope boundary, not failure of the whole method

## Outline Freeze

The old outline in [paper-outline.md](/home/zzzccc/coverup/paper/paper-outline.md) is no longer aligned with the strongest evidence because it still elevates:

- blocker explanation as the main novelty
- hierarchical memory as a headline novelty
- planner/UCB as a system-level contribution

The safer new outline should instead freeze around:

1. failure-layer-aware recovery loop
2. unified diagnosis/repair abstraction
3. bounded tool-first fixpoint
4. cross-language failure-layer study

Blocker, memory, and planner should be described as mechanisms inside that loop rather than parallel headline contributions.

## Remaining Must-Do Before Submission

1. Build a small aggregated trace table beyond individual case studies.
2. Add at least one more non-trivial slice beyond the current sanity set.
3. Add a minimal `no-tool-repair-fixpoint` or equivalent ablation to isolate the bounded-fixpoint contribution more directly.
4. Convert the current argument pack into:
   - a new paper outline
   - a draft abstract
   - a method section skeleton

## Immediate Next Step

The next paper-oriented action should be:

**rewrite the paper outline around the current thesis rather than continue extending the stale blocker/memory/planner framing.**
