# `strsim-rs` Real Smoke Audit

Date: 2026-03-25

Scope:
- project: `strsim-rs`
- seed: `42`
- original output root: `/tmp/coveragent-real-smoke`
- patched output root (`full`): `/tmp/coveragent-repair-smoke`
- patched output root (`no_planner`, `no_blocker`): `/tmp/coveragent-repair-ablation`

Compared runs:
- original `baseline`
- original `full`
- original `no_blocker`
- original `no_planner`
- patched `full`
- patched `no_planner`
- patched `no_blocker`

Patch scope before reruns:
- Rust backend now detects crate edition and treats missing `edition` in `Cargo.toml` as Rust 2015.
- Rust prompt now explicitly warns that Rust 2015 integration tests need `extern crate strsim;`.
- Rust test-code preparation now prepends `extern crate <crate>;` for Rust 2015 crates.
- Rust tool repair can also inject `extern crate <crate>;`, but that path still did not trigger in any patched rerun.

## Core Judgment

The earlier diagnosis was incomplete.

The original smoke runs suggested that:

- `full` was stalling,
- `planner` might be harmful,
- `blocker` might be harmful,
- and the agent stack might simply be over-controlling the search.

The patched reruns falsify that as the primary explanation.

After fixing Rust 2015 crate-import compatibility, all three patched agentic variants recovered:

- patched `full`: `+7.6pp`, `G=2/F=2/U=3`
- patched `no_planner`: `+11.7pp`, `G=4/F=4/U=1`
- patched `no_blocker`: `+11.7pp`, `G=5/F=8/U=3`

So the strong conclusion is:

- the dominant root cause of the original stall was the Rust 2015 import gate,
- not planner alone,
- not blocker alone,
- and not the absence of tool repair.

The more nuanced conclusion after recovery is:

- `planner` and `blocker` are now tradeoff controls, not ability gates,
- and on this slice, both may currently suppress recall relative to the patched system without them.

Tool repair remains inert, so it should not be a headline claim.

## Facts Supported by the Runs

### Original Baseline

From `/tmp/coveragent-real-smoke/results/strsim-rs_baseline_s42.json`:

- initial coverage: `85.4%`
- final coverage: `89.6%`
- delta: `+4.2pp`
- `G=2`, `F=35`, `U=1`
- cost: `$0.1013`
- wall time: `758.8s`

### Original Full

From `/tmp/coveragent-real-smoke/results/strsim-rs_full_s42.json`:

- initial coverage: `85.4%`
- final coverage: `85.4%`
- delta: `+0.0pp`
- `G=0`, `F=11`, `U=0`
- cost: `$0.0620`
- wall time: `567.5s`
- memory lessons: `2`
- planner pulls: `11`

From `/tmp/coveragent-real-smoke/traces/strsim-rs_full_s42.jsonl`:

- total attempts: `11`
- outcomes: `11 F`
- diagnostic categories: `11 import`
- phases: `11 compile`
- top error codes: `E0432 x10`, `E0425 x1`
- blocker injected attempts: `11`
- memory injected attempts: `0`
- tool repair attempts: `0`

### Original No Planner

From `/tmp/coveragent-real-smoke/results/strsim-rs_no_planner_s42.json`:

- initial coverage: `85.4%`
- final coverage: `85.4%`
- delta: `+0.0pp`
- `G=0`, `F=27`, `U=2`
- cost: `$0.1335`
- wall time: `588.4s`
- memory lessons: `3`

From `/tmp/coveragent-real-smoke/traces/strsim-rs_no_planner_s42.jsonl`:

- total attempts: `29`
- outcomes: `27 F / 2 U`
- diagnostic categories: `26 import`, `2 unknown`, `1 type`
- phases: `27 compile / 2 coverage`
- top error codes: `E0432 x26`, `E0277 x1`
- blocker injected attempts: `24`
- memory injected attempts: `0`
- tool repair attempts: `0`

### Original No Blocker

From `/tmp/coveragent-real-smoke/results/strsim-rs_no_blocker_s42.json`:

- initial coverage: `85.4%`
- final coverage: `85.4%`
- delta: `+0.0pp`
- `G=0`, `F=20`, `U=0`
- cost: `$0.0967`
- wall time: `659.5s`
- memory lessons: `1`
- planner pulls: `20`

### Patched Full

From `/tmp/coveragent-repair-smoke/results/strsim-rs_full_s42.json`:

- initial coverage: `85.4%`
- final coverage: `93.0%`
- delta: `+7.6pp`
- `G=2`, `F=2`, `U=3`
- cost: `$0.0463`
- wall time: `439.8s`
- memory lessons: `4`
- planner pulls: `7`
- repair tool fixes: `0`

From `/tmp/coveragent-repair-smoke/traces/strsim-rs_full_s42.jsonl`:

- total attempts: `7`
- outcomes: `2 G / 2 F / 3 U`
- diagnostic categories: `5 unknown`, `1 panic`, `1 type`
- phases: `5 coverage / 2 compile`
- blocker injected attempts: `7`
- memory injected attempts: `5`
- tool repair attempts: `0`

### Patched No Planner

From `/tmp/coveragent-repair-ablation/results/strsim-rs_no_planner_s42.json`:

- initial coverage: `85.4%`
- final coverage: `97.1%`
- delta: `+11.7pp`
- `G=4`, `F=4`, `U=1`
- cost: `$0.0599`
- wall time: `409.7s`
- memory lessons: `4`
- planner pulls: `0`
- repair tool fixes: `0`

From `/tmp/coveragent-repair-ablation/traces/strsim-rs_no_planner_s42.jsonl`:

- total attempts: `9`
- outcomes: `4 G / 4 F / 1 U`
- diagnostic categories: `5 unknown`, `3 panic`, `1 type`
- phases: `5 coverage / 4 compile`
- blocker injected attempts: `9`
- memory injected attempts: `5`
- tool repair attempts: `0`

### Patched No Blocker

From `/tmp/coveragent-repair-ablation/results/strsim-rs_no_blocker_s42.json`:

- initial coverage: `85.4%`
- final coverage: `97.1%`
- delta: `+11.7pp`
- `G=5`, `F=8`, `U=3`
- cost: `$0.0268`
- wall time: `458.4s`
- memory lessons: `5`
- planner pulls: `16`
- repair tool fixes: `0`

From `/tmp/coveragent-repair-ablation/traces/strsim-rs_no_blocker_s42.jsonl`:

- total attempts: `16`
- outcomes: `5 G / 8 F / 3 U`
- diagnostic categories: `8 unknown`, `5 panic`, `3 type`
- phases: `8 coverage / 8 compile`
- top error codes: `E0277 x2`
- blocker injected attempts: `0`
- memory injected attempts: `6`
- tool repair attempts: `0`

### Generated Tests

From `/tmp/coveragent-real-smoke/workspace/strsim-rs/tests/coverup_001_test.rs` and `/tmp/coveragent-real-smoke/workspace/strsim-rs/tests/coverup_002_test.rs`:

- successful generated tests in the recovered runs begin with `extern crate strsim;`

## Direct Comparison

### Original Failure Mode vs Patched Failure Mode

Original agentic runs:

- `full`, `no_planner`, and `no_blocker` all had `+0.0pp`
- the dominant failure mode was compile-time import failure
- repair never activated
- memory never injected early enough to matter

Patched agentic runs:

- all three variants achieved positive coverage gain
- failure composition shifted away from import-only compile failure
- successful coverage runs happened early
- repair still never activated

This is strong evidence that the patch removed an entry barrier rather than improving late-stage repair.

### Patched Variant Comparison

Coverage:

- patched `full`: `93.0%` (`+7.6pp`)
- patched `no_planner`: `97.1%` (`+11.7pp`)
- patched `no_blocker`: `97.1%` (`+11.7pp`)

Search shape:

- patched `full`: fewer attempts, lower recall
- patched `no_planner`: moderate attempts, best wall time among patched variants
- patched `no_blocker`: most attempts, highest `G`, highest churn

Cost:

- patched `full`: `$0.0463`
- patched `no_planner`: `$0.0599`
- patched `no_blocker`: `$0.0268`

Interpretation that is supported:

- planner is not necessary for recovery on this slice
- blocker is not necessary for recovery on this slice
- removing planner improved recall on this slice
- removing blocker improved recall on this slice
- blocker still changes behavior: it reduces exploration and seems to suppress both `G` and failure churn

Interpretation that is not yet supported:

- planner is generally harmful
- blocker is generally harmful
- no_blocker is globally best
- no_planner is globally best

## Supported Facts / Inferences / Hypotheses / High-Risk Claims

### Facts Supported by Code and Runs

- original `full`, `no_planner`, and `no_blocker` all failed to produce any gain on `strsim-rs`
- those original failures were dominated by Rust import errors
- patched `full`, `no_planner`, and `no_blocker` all recovered
- patched `no_planner` and patched `no_blocker` both outperformed patched `full` on line coverage
- tool repair stayed inactive in every patched rerun
- successful recovered tests contain `extern crate strsim;`

### Strong Inferences

- Rust 2015 crate-import compatibility was the primary gate that prevented productive search on this slice
- the recovery is not attributable to planner alone or blocker alone because both disabled variants also recovered
- the active source of recovery is most plausibly the edition-aware prompt/backend normalization layer
- after the gate is removed, planner and blocker appear to trade recall against control rather than enabling success

### Hypotheses Requiring Further Verification

- how much of the recovery comes from prompt guidance alone vs backend canonicalization alone
- whether the patched `full` underperforming patched `no_planner` is stable across seeds
- whether blocker consistently reduces recall on other projects
- whether this import-gate effect appears on other Rust crates in the benchmark

### High-Risk or Currently Unsupported Claims

- “tool repair solved the Rust failure mode”
  - not supported
- “planner was the original root cause”
  - no longer supported
- “blocker was the original root cause”
  - no longer supported
- “the full closed loop is what produced the recovery”
  - too broad; current evidence points to a narrower normalization effect
- “no_planner” or “no_blocker” should be the final recommended configuration
  - not yet supported beyond this slice

## Risks

### Evaluation Risk

This is still one project and one seed for the patched matrix.

Reviewers can still ask:

- is `strsim-rs` special because it is implicitly Rust 2015?
- do these rankings persist on another Rust project?
- do these rankings persist across seeds?

### Methodology Risk

The causal attribution is only partially isolated.

We now know:

- repair did not cause the recovery
- planner/blocker removal is not required for recovery

We still do not know:

- prompt-only vs backend-only contribution

### Writing Risk

We should not write:

- “repair solves Rust compile failures”
- “planner is harmful”
- “blocker is harmful”

The defensible writing line is:

- “language-aware compatibility normalization can be a prerequisite for productive agentic test generation; once that prerequisite is satisfied, higher-level controls such as planning and blocker guidance become second-order tradeoff choices.”

## Most Valuable Next Steps

1. Run one more Rust project with patched `full`.
   - Goal: test whether the recovery mechanism generalizes beyond `strsim-rs`.

2. Isolate prompt-only vs backend-only on `strsim-rs`.
   - Goal: separate the two active ingredients of the recovery.

3. If another Rust project also shows recovery, rerun `no_planner` there before rerunning `no_blocker`.
   - Current evidence makes planner the higher-value tradeoff to audit first.

4. Add failure-mode composition and tool-call churn to the experiment tables.
   - The bottleneck moved from import failure to reasoning/tool-usage churn on hard segments.

5. Do not elevate repair in the paper narrative yet.
   - On current evidence, repair exists but is not the reason the system recovered.

## Submission Audit

### Novelty Audit

The novelty story is now sharper:

- not “agent features generally help”
- more plausibly “language-aware normalization of compile/execution constraints is necessary before adaptive agent loops can help”

That is more specific and more defensible.

### Methodology Audit

Methodology improved materially because:

- we found a concrete mechanistic failure mode
- we implemented a targeted fix
- the fix changed both outcome quality and failure composition
- the fix recovered multiple ablations, not just one configuration

But attribution is still incomplete.

### Evaluation Audit

Evaluation is much stronger than before:

- before: three agentic variants all stalled at `+0.0pp`
- after: three patched agentic variants all recover, two of them reaching `+11.7pp`

Still not submission-ready because:

- only one project has the patched ablation matrix
- only one seed has been run

### Writing Audit

The paper story should now pivot from:

- “our agent stack beats baseline”

to:

- “our original system stalled on a language-specific compatibility gate; after removing that gate, the agentic variants become productive, and the remaining design question becomes how to trade recall against control.”

That is a more coherent and reviewer-resistant narrative than the earlier version.
