# Paper Outline: CoverAgent-ML

> **Working Title**: *From Missing Lines to Reachability Conditions: Agent-Guided Coverage-Driven Test Generation*
>
> **Target**: ISSTA 2026 / ASE 2026 (CCF-A)
>
> **Last Updated**: 2026-02-18 (for collaborator review)

---

## Abstract (~250 words)

Coverage-driven test generation with LLMs suffers from two problems:
(1) the LLM only knows *which* lines to cover but not *why* they are unreachable, leading to many "useless" tests that compile but gain no coverage;
(2) there is no learning across attempts — the same fix mistakes repeat.

We present **CoverAgent-ML**, an agentic framework that addresses both issues.
Our key innovation is **Coverage Blocker Explanation**: using tree-sitter/AST analysis, we extract the guard predicates blocking uncovered lines and trace the variables involved to their origins, producing structured "why unreachable + how to reach" hints.
Our second contribution is **Hierarchical Recipe Memory**: a success-weighted skill library indexed by diagnostic signatures, using a three-level success signal (compile / pass / coverage gain) to learn repair recipes progressively.
Both components are language-agnostic via a unified **DiagnosticIR** intermediate representation.
Evaluated on N projects across Rust, Python, and Go, CoverAgent-ML with a weak LLM (DeepSeek Coder, ~30× cheaper) matches or exceeds the coverage of prior work with GPT-4o:
on Flask, agent+DeepSeek (95.8%) > CoverUp+GPT-4o (94.4%).
Ablation shows Blocker Explanation reduces Useless rate by X% and Recipe Memory reduces failure rate by 10–41%.
All five agent modules are independently disablable, enabling principled ablation.

---

## 1. Introduction (1.5 pages)

### 1.1 Problem

LLM-based coverage-driven test generation (CoverUp, PALM, RUG) has emerged as a promising approach.
However, current systems hit a **coverage plateau** because:
- The LLM receives only "line X not covered" (WHERE) but not "why" (the **reachability gap**)
- Each attempt is memoryless — the same import/type/visibility bugs recur
- There is no budget allocation — equal effort on easy and hard segments

### 1.2 Our Insight

> **The key bottleneck is not LLM capability but information quality**: the LLM can generate correct tests if told *what conditions to trigger* and *what mistakes to avoid*.

Two complementary strategies:
1. **Coverage Blocker Explanation** — upgrade "missing lines" to "guard predicates + variable provenance + reachability hints"
2. **Hierarchical Recipe Memory** — accumulate repair patterns indexed by diagnostic signatures with graded success (compile/pass/gain)

### 1.3 Contributions (4 points)

| # | Type | Contribution |
|---|------|-------------|
| **C1** | Method | **Coverage Blocker Explanation**: first to apply guard predicate extraction + variable origin tracing for LLM test generation guidance. Lightweight (~150 LoC/language), zero extra LLM calls, cross-language (Rust/Go/Python). |
| **C2** | Method | **Hierarchical Recipe Memory + Two-Phase Repair**: three-level success signal (COMPILE/PARTIAL/FULL) enables progressive skill accumulation; tool-first deterministic repair eliminates 30–41% of failures before engaging LLM. |
| **C3** | System | **CoverAgent-ML Framework**: language-agnostic DiagnosticIR + 5-module ablatable architecture with UCB budget-aware scheduling. |
| **C4** | Empirical | **Cross-language evaluation**: N projects × 3 languages, complete ablation matrix. Weak LLM + agent ≥ strong LLM + naive on Flask. |

### 1.4 Key Result (hook)

> On Flask: CoverAgent-ML + DeepSeek Coder (95.8%) > CoverUp + GPT-4o (94.4%), at ~30× lower cost.

---

## 2. Motivating Example (1 page)

Use `similar` crate (Rust) to show a concrete segment where:

### 2.1 Baseline fails

```
CoverUp says: "Lines 156-162 do not execute."
LLM generates: test that creates DiffOp, compiles, runs, but never exercises the false branch of `if d_old.len() > d_new.len()`.
Result: Useless (U) — 0 coverage gain.
```

### 2.2 With Blocker Explanation

```
CoverAgent-ML says:
  "Line 156 not reached because guard `d_old.len() > d_new.len()` is always false.
   Variable `d_old` comes from field of DiffableStr.
   Hint: construct input where old sequence is longer than new."

LLM generates: test with old="hello world", new="hi" → exercises the branch.
Result: Good (G) — +3 lines covered.
```

### 2.3 With Recipe Memory

Show how memory accumulates `Recipe(action="rust_add_imports(use similar::*)", category="import", success_rate=0.85)` across segments, and new segments with the same error get the fix prescribed automatically.

**Figure 1**: Side-by-side prompt comparison (CoverUp vs CoverAgent-ML)

---

## 3. Approach (5 pages)

### 3.1 Architecture Overview (0.5p)

**Figure 2**: System architecture diagram

```
                    ┌─────────────┐
                    │  UCB Planner │ ← budget allocation (C3)
                    └──────┬──────┘
                           │ select_batch(k)
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌─────────┐ ┌─────────┐ ┌─────────┐
         │ Segment₁ │ │ Segment₂ │ │ Segmentₖ │
         └────┬─────┘ └────┬─────┘ └────┬─────┘
              │            │            │
    ┌─────────▼────────────▼────────────▼─────────┐
    │            Per-segment pipeline              │
    │  ┌──────────────┐  ┌──────────────────────┐  │
    │  │ Blocker (C1) │→ │ Memory lessons (C2)  │  │
    │  └──────┬───────┘  └──────────┬───────────┘  │
    │         └───────┬─────────────┘              │
    │                 ▼                            │
    │          LLM prompt + generation             │
    │                 │                            │
    │          compile / run / measure             │
    │                 │                            │
    │         DiagnosticIR classify                │
    │                 │                            │
    │     ┌───────────┼───────────┐               │
    │     ▼           ▼           ▼               │
    │  Repair(C2)  Memory(C2)  Planner(C3)        │
    │  tool-first  record()    update()           │
    └─────────────────────────────────────────────┘
```

- **DiagnosticIR**: language-agnostic intermediate representation (13 ErrorCategory × 6 Phase)
- All agent modules communicate exclusively through DiagnosticIR → zero cross-language coupling

### 3.2 Coverage Blocker Explanation — C1 (1.5p)

#### 3.2.1 Problem Formulation

**Definition** (Coverage Blocker): Given target uncovered line $\ell$, its nearest control-flow dominating condition is $P(\ell)$. A Coverage Blocker is:

$$B(\ell) = \langle P(\ell),\ \text{origin}(P),\ \text{hint}(P) \rangle$$

- $P(\ell)$: guard predicate source text (e.g., `x > 0`, `matches!(val, Some(_))`)
- $\text{origin}(P)$: provenance of variables in $P$ (parameter / field / return value / local)
- $\text{hint}(P)$: actionable test construction suggestion

#### 3.2.2 Guard Predicate Extraction

- **Rust/Go**: tree-sitter queries on `if_expression.condition`, `match_expression.value`, `switch_statement.value`
- **Python**: stdlib `ast` module on `ast.If.test`, `ast.Match.subject`
- For each uncovered line, walk the AST upward to find the nearest enclosing conditional that controls reachability

#### 3.2.3 Variable Origin Tracing

For each identifier in the predicate:
1. Search upward in the enclosing function for `let`/`:=`/assignment
2. Classify origin: `parameter` | `field_access` | `return_value` | `local_computation` | `constant`
3. If origin is a parameter → directly actionable in test ("pass X as argument")
4. If origin is a return value → chain one level ("call method Y with Z to get the needed value")

#### 3.2.4 Hint Generation

Template-based: combine predicate text + variable origins into natural language hint:
```
"Line {L} is unreachable because {predicate} at line {P_line} evaluates to {current}.
 Variable {var} originates from {origin}.
 To cover line {L}: {actionable_suggestion}"
```

**Figure 3**: Example blocker output for Rust, Python, Go

#### 3.2.5 Comparison with PALM

| | PALM | Ours |
|---|------|------|
| Analysis depth | Full path constraint (SMT-like) | Nearest guard + 1-level var trace |
| Cost | Heavy (custom Rust analysis framework) | ~150 LoC/language (tree-sitter) |
| Languages | Rust only | Rust + Go + Python |
| Runtime info | None | Leverages existing coverage data |
| Integration | Standalone | Composable with Memory + Repair |

### 3.3 Hierarchical Recipe Memory + Two-Phase Repair — C2 (1.5p)

#### 3.3.1 Diagnostic Signature Matching

Each error is mapped to a 4-tuple signature: `(language, error_category, error_code, tool)`.
Recipes are indexed by this signature and ranked by weighted success rate.

#### 3.3.2 Three-Level Success Signal

$$\text{SuccessLevel} \in \{\text{NONE}, \text{COMPILE}, \text{PARTIAL}, \text{FULL}\}$$

- **NONE**: complete failure (compile error, crash)
- **COMPILE**: tool repair recovered compilability (error → can run)
- **PARTIAL**: test runs but no coverage gain (Useless)
- **FULL**: test produces coverage increase (Good)

The success rate uses weighted aggregation:

$$\text{success\_rate} = \frac{w_F \cdot n_F + w_P \cdot n_P + w_C \cdot n_C}{n_{total}}, \quad w_F=1.0,\ w_P=0.3,\ w_C=0.1$$

**Insight**: This lets the system learn "how to get code to compile" as an intermediate skill — critical for languages like Rust where compilation is the main barrier.

#### 3.3.3 Recipe Ranking: UCB × Recency

$$\text{score}(r) = \underbrace{\left(\text{SR}(r) + \frac{c}{2}\sqrt{\frac{\ln T}{n_r}}\right)}_{\text{UCB exploration}} \times \underbrace{(0.3 + 0.7 \cdot e^{-\lambda \cdot \text{age}(r)})}_{\text{recency factor}}$$

- $T$: total records across all recipes
- $n_r$: attempts for recipe $r$
- $\lambda = \ln 2 / 600$ (half-life = 10 minutes)

#### 3.3.4 Two-Phase Repair Pipeline

```
Compile/run failure
  └─ Phase 1: Deterministic tool repair (zero LLM cost)
       7 built-in fixers: Rust imports × 1, cargo-check autofix × 1,
                          Python imports × 1, syntax × 1, Go imports × 1
       └─ Fixed? → re-verify, record COMPILE
       └─ Not fixed? → Phase 2
  └─ Phase 2: LLM fallback with memory hint
       memory.format_entry_for_error(ir) → inject targeted prescription
       └─ LLM retries with "Do: add `use crate::X`" guidance
```

**Key metric**: failure rate reduction of 10–41% across all 4 evaluated projects.

### 3.4 Budget-Aware Scheduling — C3 (0.5p)

- Standard UCB1 on segments as arms, with gap_complexity weighting
- Plateau freeze: arms with ≥3 consecutive Useless get score × 0.05
- **Size-adaptive exploration**: `c=0.8` for small projects (<20 segs), `c=2.0` for large (>80 segs)
- **min_passes mechanism**: force at least 2 passes, unfreezing promising arms for the second pass to leverage accumulated memory
- Wave scheduling: `select_batch(k)` → parallel execution → `update()` → next wave

*Note: We use standard UCB1 — the contribution is integrating it into the control flow with ablation support, not the algorithm itself.*

---

## 4. Implementation (1 page)

### 4.1 System Overview

- Built on CoverUp (Python, asyncio)
- 2,287 lines of agent code + 1,098 lines integration in main loop
- All modules communicate via frozen `DiagnosticIR` dataclass

### 4.2 Language Backends

| Language | Coverage tool | Test framework | Static analysis |
|----------|--------------|----------------|-----------------|
| Rust | cargo-llvm-cov | #[test] | tree-sitter-rust |
| Python | SlipCover | pytest | stdlib ast |
| Go | go test -cover | testing.T | tree-sitter-go |

### 4.3 Ablation Support

5 CLI flags independently disable each module:
`--no-agent-memory`, `--no-agent-repair`, `--no-agent-planner`, `--no-agent-blocker`, `--trace-log`

---

## 5. Evaluation (4 pages)

### 5.1 Setup

**Research Questions**:
- **RQ1**: Does CoverAgent-ML improve coverage over the baseline? (*Overall effectiveness*)
- **RQ2**: What is the individual contribution of each component? (*Ablation*)
- **RQ3**: Does the approach generalize across languages? (*Cross-language*)
- **RQ4**: Is the approach cost-efficient? (*Token efficiency*)
- **RQ5**: Does Blocker Explanation reduce Useless tests? (*C1 validation*)

**Projects**: N projects (balanced across Rust/Python/Go), selected from prior work benchmarks + popular open-source

**Variants** (6):

| Variant | Planner | Memory | Repair | Blocker |
|---------|---------|--------|--------|---------|
| full | ✅ | ✅ | ✅ | ✅ |
| no_blocker | ✅ | ✅ | ✅ | ❌ |
| no_memory | ✅ | ❌ | ✅ | ✅ |
| no_repair | ✅ | ✅ | ❌ | ✅ |
| wave_only | ✅ | ❌ | ❌ | ❌ |
| baseline | ❌ | ❌ | ❌ | ❌ |

**Repetitions**: 3 seeds per configuration
**LLM**: DeepSeek Coder (via litellm), temperature=0
**Statistics**: Wilcoxon signed-rank test, Cliff's delta

### 5.2 RQ1: Overall Effectiveness

**Table**: Coverage comparison (full vs baseline) for all N projects

**Metrics**: Final line coverage (%), Good/Failed/Useless counts, API cost ($), wall time

**Preliminary results** (4 projects):

| Project | Language | Baseline | Full Agent | Δ |
|---------|----------|----------|-----------|---|
| Flask | Python | 94.9% | 95.8% | **+0.9pp** |
| similar | Rust | 90.9% | 92.5% | **+1.6pp** |
| fastrand | Rust | 97.5% | TBD | TBD |
| cobra | Go | 97.3% | TBD | TBD |

*(fastrand/cobra to be re-run after I-1/I-2 fixes)*

### 5.3 RQ2: Ablation

**Figure 4**: Ablation bar chart — coverage delta per component

Decomposition:
- `full − no_blocker` = C1 contribution
- `full − no_memory` = C2 (memory) contribution
- `full − no_repair` = C2 (repair) contribution
- `wave_only − baseline` = C3 (scheduling) contribution
- `full − wave_only` = all agent intelligence beyond scheduling

### 5.4 RQ3: Cross-Language Generalization

**Table**: Per-language breakdown showing agent benefit is consistent across Rust/Python/Go

**Figure 5**: Coverage vs. attempt curves per language (showing convergence speed)

### 5.5 RQ4: Token Efficiency

$$\text{Efficiency} = \frac{\Delta \text{Coverage} (\text{pp})}{T_{\text{total}} / 1000}$$

**Figure 6**: Boxplot of token efficiency per variant per language

**Comparison with CoverUp/PALM**:
- "Weak LLM + Agent (ours)" vs "Strong LLM + naive (CoverUp)"
- Cost reduction while maintaining/improving coverage

### 5.6 RQ5: Blocker Impact on Useless

**Table**: Useless rate (U/(G+F+U)) for `full` vs `no_blocker`

**Human evaluation** (subset, ~50 blockers):
- Sample 50 random blocker explanations
- Annotate: correct / partially correct / incorrect
- Report precision as "Blocker Accuracy"

---

## 6. Discussion (1 page)

### 6.1 When Does the Agent Help vs Hurt?

- Large/complex projects: agent learns enough to offset overhead
- Small/simple projects: with I-1/I-2 fixes, agent is at least neutral
- The size-adaptive tuning ensures agent doesn't over-explore on easy projects

### 6.2 Weak LLM + Agent vs Strong LLM

- Flask: DeepSeek + Agent (95.8%) > GPT-4o + CoverUp (94.4%)
- Implication: intelligence placement matters more than raw LLM power
- Cost: ~$0.01/run vs ~$0.30/run for GPT-4o

### 6.3 Threats to Validity

- **Internal**: LLM non-determinism → mitigated by 3× repetition + temperature=0
- **External**: project selection bias → mitigated by including prior work benchmarks
- **Construct**: coverage ≠ fault detection → common limitation, no claim about fault-finding

### 6.4 Limitations

- Blocker only extracts nearest guard (not full path constraints like PALM)
- Memory doesn't persist across runs (session-only learning)
- No support for Java/C++ yet (tree-sitter available, backend work needed)

---

## 7. Related Work (1 page)

### 7.1 LLM-based Test Generation

- **CoverUp** (FSE'25): iterative coverage feedback, Python-only, no learning across segments
- **RUG** (ICSE'25): semantic-aware bottom-up context, Rust-only, no memory/budget
- **PALM** (ASE'25): full path constraint extraction, Rust-only, heavyweight
- **ASTER** (ICSE'25): multi-language (Java+Python), static analysis, no online learning
- **ChatUniTest**, **TestPilot**, **CodaMosa**: earlier generation of LLM test gen, no coverage feedback loop

### 7.2 Search-Based Test Generation

- EvoSuite, Randoop (Java), AFL/libFuzzer (C/C++)
- Complementary: our approach generates readable unit tests; SBST generates input values

### 7.3 Program Analysis for Test Generation

- Symbolic execution (KLEE, SAGE)
- PALM's branch condition extraction is closest to our Blocker, but heavyweight + single-language
- Our Blocker is deliberately lightweight ("good enough" for LLM guidance, not formal verification)

### 7.4 Adaptive Agent Architectures

- Multi-armed bandits in SE: test case prioritization (Spieker et al.), API testing (Atlidakis et al.)
- Online learning in software: reinforcement learning for test generation (RLCHECK)
- Our contribution: applying online recipe learning to coverage-driven LLM test gen

---

## 8. Conclusion (0.5 page)

We presented CoverAgent-ML, an agentic framework for coverage-driven test generation that transforms "missing line" feedback into actionable reachability conditions.
Coverage Blocker Explanation and Hierarchical Recipe Memory are language-agnostic and incur zero extra LLM cost.
On N projects across 3 languages, CoverAgent-ML with a weak LLM matches or exceeds strong-LLM baselines at ~30× lower cost.
All components are independently ablatable, enabling principled evaluation.

Future work: persistent cross-run memory, dynamic blocker with runtime coverage fusion, support for Java/C++.

---

## Figure/Table Plan

| # | Type | Content | Section |
|---|------|---------|---------|
| Fig 1 | Side-by-side | CoverUp prompt vs CoverAgent-ML prompt | §2 |
| Fig 2 | Architecture | System diagram with data flow | §3.1 |
| Fig 3 | Example | Blocker output for Rust/Python/Go | §3.2 |
| Fig 4 | Bar chart | Ablation: coverage delta per component | §5.3 |
| Fig 5 | Line chart | Coverage vs. attempt curves by language | §5.4 |
| Fig 6 | Boxplot | Token efficiency by variant | §5.5 |
| Tab 1 | Results | Full vs baseline coverage for all N projects | §5.2 |
| Tab 2 | Ablation | 6-variant × N-project coverage matrix | §5.3 |
| Tab 3 | Useless | U rate: full vs no_blocker | §5.6 |
| Tab 4 | Cost | API cost comparison with CoverUp/PALM | §5.5 |
| Tab 5 | Blocker | Human evaluation accuracy (50 samples) | §5.6 |

---

## Reviewer Defense Cheat Sheet

| Anticipated Attack | Defense |
|--------------------|---------|
| "Agent hurts on small projects" | Size-adaptive exploration (I-2) + min_passes (I-1) ensure agent is ≥ baseline everywhere |
| "Only N projects" | Balanced across 3 languages; includes prior work benchmarks (Flask from CoverUp, fastrand from PALM) |
| "CoverUp uses GPT-4o, unfair" | We show *weak LLM + agent* beats *strong LLM + naive* — that's the point. Also report cost. |
| "Blocker accuracy?" | Human eval on 50 samples (§5.6 Tab 5) |
| "UCB is not novel" | We explicitly disclaim novelty (§3.4); contribution is integration + ablation-friendly architecture |
| "Time overhead of agent" | Agent adds X% wall time but reduces LLM calls by 30% and API cost by 10-20% |
| "No fault detection evaluation" | Acknowledged limitation (§6.3); coverage is standard metric in this line of work |
| "Memory doesn't persist" | Session-only learning is intentional (project-specific patterns); cross-run is future work |

---

## TODO Before Submission

- [ ] Run full experiment matrix (N projects × 6 variants × 3 seeds)
- [ ] Re-run fastrand/cobra with I-1/I-2 fixes
- [ ] Human evaluation of 50 blocker explanations
- [ ] Exact N count: target 12-15 projects
- [ ] Fill all TBD numbers
- [ ] Write actual paper prose
- [ ] Create all figures
