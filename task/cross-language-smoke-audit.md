# Cross-Language Smoke Audit

Date: 2026-03-25

## Scope

- Goal: check whether the current difficulty is mainly a Rust-specific issue or a broader multi-language weakness.
- Evidence sources:
  - Rust `strsim-rs` and `similar` targeted/smoke runs from earlier audits
  - Python `click` targeted run on `decorators.py:420-530`
  - Go `cobra` targeted run on `command.go:1749-1759` (`ResetFlags`)

## Core Judgment

- The current system is **not uniformly blocked across languages**.
- Rust remains the hardest slice we have seen so far, especially on language/API-shape-heavy segments.
- Python is no longer blocked by infrastructure, but is currently stalling on framework-specific public-API and exception-shape reasoning.
- Go is not uniformly blocked, but its earlier one-slice success is not yet stable enough to treat as a robust method win.

## Facts

### Rust

- `strsim-rs` originally stalled on a Rust-2015 import gate; after edition-aware repair/prompting, agentic variants recovered and produced real gains.
- `similar` moved past early compile gates, but later hard slices were dominated by semantic/panic and API-shape failures.
- On targeted semantic-recovery ablations, the prompt path changed, but we did not yet obtain a clear outcome lift.

### Python (`click`)

- Before multi-language exploration, Python evaluation was polluted by three infra bugs:
  - test subprocesses ran in the wrong cwd
  - slipcover coverage keys were relative and broke segmentation
  - `pytest-repeat` was assumed to exist even when unavailable
- Those issues are now fixed in:
  - `src/coverup/utils.py`
  - `src/coverup/testrunner.py`
  - `src/coverup/languages/python_backend.py`
- Unpatched targeted run on `click/src/click/decorators.py:420-530` failed with:
  - attempt 1: `assertion`
  - attempt 2: `syntax`
  - attempt 3: `type`
- After adding Python `signature/API-shape recovery` in `src/coverup/prompt/gpt_v2.py`, the same targeted slice changed failure composition to:
  - attempt 1: `visibility`
  - attempt 2: `visibility`
  - attempt 3: `visibility`
- The patched run still ended with `Too many attempts, giving up`, so this is **failure-shape improvement**, not coverage improvement.

### Go (`cobra`)

- `go test ./...` on `cobra@v1.8.1` passed cleanly before CoverUp runs.
- Dry-run on `command.go` succeeded and selected meaningful uncovered segments.
- Real targeted run on `command.go:1749-1759` (`ResetFlags`) produced:
  - initial coverage: `91.2%`
  - final coverage: `91.5%`
  - counters: `G=1, F=2, U=0`
  - trace: `/tmp/cobra-full-resetflags.jsonl`
- Trace sequence:
  - attempt 1: `visibility`
  - attempt 2: `unknown`
  - attempt 3: `G`
- The successful test was saved as:
  - `/tmp/coveragent-crosslang/cobra-full-run1-1774426600/coverup_001_test.go`

### Go (`cobra`) Follow-Up: Same Slice With Current Instrumentation

- fresh workspace:
  - `/tmp/coveragent-crosslang/cobra-full-run2-1774443683`
- dry-run confirmed the same targeted slice and baseline:
  - initial coverage: `91.2%`
  - selected segment: `/tmp/coveragent-crosslang/cobra-full-run2-1774443683/command.go:1749-1759`
- real rerun:
  - trace: `/tmp/cobra-resetflags-v2.jsonl`
  - log: `/tmp/cobra-resetflags-v2.log`
  - final coverage: `91.2%`
  - summary counters: `F=3, G=0, U=0`

Trace facts:

- attempt 1:
  - `action=llm`
  - `repair_passes=0`
  - terminal category `assertion`
- attempt 2:
  - `action=llm`
  - `repair_passes=0`
  - terminal category `assertion`
- attempt 3:
  - `action=llm`
  - `repair_passes=0`
  - terminal category `visibility`

Observed failure content:

- repeated assertion failures were driven by wrong exported behavior assumptions such as:
  - expecting parse errors for `--localroot`
  - expecting `flagErrorBuf` contents under the wrong setup
- the final failure exposed a stricter public-surface issue:
  - unused locals (`declared and not used`)
  - nonexistent getters like `cmd.flags.Output()` and `cmd.pflags.Output()`

Interpretation:

- on this Go slice, the new bounded fixpoint mechanism was present but dormant:
  - no tool repairs fired
  - no fixpoint pass was used
- so the current Go bottleneck is not repair orchestration itself, but the absence of useful Go-side public-API / cleanup operators

### Go (`cobra`) Follow-Up: Prompt + Operator Update

After the failed rerun above, two changes were introduced:

- prompt-level guardrails in [`gpt_go_v1.py`](/home/zzzccc/coverup/src/coverup/prompt/gpt_go_v1.py) now say more explicitly:
  - do not expect pre-reset flags to survive a fresh `FlagSet`
  - remove unused locals rather than treating them as meaningful assertions
  - stop using nonexistent accessors such as `Output()`
- minimal Go operators were added in [`repair.py`](/home/zzzccc/coverup/src/coverup/agents/repair.py):
  - unused-binding cleanup
  - invalid `Output()` accessor block removal

Then the same `ResetFlags` slice was rerun again:

- workspace:
  - `/tmp/coveragent-crosslang/cobra-full-run3-1774445749`
- trace:
  - `/tmp/cobra-resetflags-v3.jsonl`
- log:
  - `/tmp/cobra-resetflags-v3.log`
- saved test:
  - `/tmp/coveragent-crosslang/cobra-full-run3-1774445749/coverup_001_test.go`

Facts:

- final coverage improved from `91.2%` to `91.5%`
- terminal trace is a single attempt:
  - `attempt 1: G`
  - `action=llm`
  - `repair_passes=0`
  - `tool_fixes=[]`
- the generated test now avoids the earlier failure modes:
  - it no longer assumes pre-reset flags remain parsable
  - it no longer calls nonexistent accessors like `cmd.flags.Output()`
  - it checks cleared flags via `Lookup(...) == nil` and buffer size via `Len()`

Interpretation:

- this is a real recovery on the same Go slice
- but the causal story matters:
  - the win did **not** come from tool repair absorption
  - the win came from better public-surface reasoning in the first generated test
- so for Go, the currently effective layer is still closer to prompt-level public-API grounding than to tool-side recovery

### Go (`cobra`) Follow-Up: `ResetFlags` Under The Current Recovery Loop

After the later Go operator work on `DebugFlags`, the simpler `ResetFlags` slice was revisited to test whether the positive Go story replicates beyond one hard slice:

- `v4` workspace:
  - `/tmp/coveragent-crosslang/cobra-reset-run4-1774451174`
- `v4` trace:
  - `/tmp/cobra-resetflags-v4.jsonl`
- `v4` log:
  - `/tmp/cobra-resetflags-v4.log`
- `v5` workspace:
  - `/tmp/coveragent-crosslang/cobra-reset-run5-1774451430`
- `v5` trace:
  - `/tmp/cobra-resetflags-v5.jsonl`
- `v5` log:
  - `/tmp/cobra-resetflags-v5.log`
- `v6` workspace:
  - `/tmp/coveragent-crosslang/cobra-reset-run6-1774451691`
- `v6` trace:
  - `/tmp/cobra-resetflags-v6.jsonl`
- `v6` log:
  - `/tmp/cobra-resetflags-v6.log`
- `v6` saved test:
  - `/tmp/coveragent-crosslang/cobra-reset-run6-1774451691/coverup_001_test.go`

Facts:

- `v4` no longer behaved like the earlier prompt-only `ResetFlags` win:
  - all three attempts entered `tool_repair+llm`
  - attempt 1 removed invalid `Output()` accessor assertions
  - but the next failure exposed the same family again through invalid `ErrorHandling()` accessor usage
  - final outcome stayed flat:
    - `91.2% -> 91.2%`
- this motivated a broader operator change:
  - invalid `FlagSet` accessor cleanup now removes assertion blocks using:
    - `Output()`
    - `ErrorHandling()`
    - `Name()`
  - code location:
    - `src/coverup/agents/repair.py`
- `v5` then showed a different but related failure path:
  - the first attempt now failed on invalid `Name()` accessor usage
  - later attempts moved into assertion failures about `flagErrorBuf` / `unknown flag`
  - final outcome still stayed flat:
    - `91.2% -> 91.2%`
- `v6` then recovered cleanly:
  - terminal trace is a single attempt:
    - attempt 1: `action=llm`, outcome `G`
  - final coverage improved:
    - `91.2% -> 91.5%`
  - all target `ResetFlags` lines were gained

Interpretation:

- this is useful for the paper in two different ways:
  - `DebugFlags` is the stronger evidence for **repair-assisted benefit**
  - `ResetFlags` is now a better evidence line for **Go slice instability and recovery-layer interaction**
- more concretely:
  - `v4` showed repair engagement on a simpler slice
  - `v5` showed that invalid-accessor failures form a family, not a one-off bug
  - `v6` showed the same slice can still recover positively once that family is better understood
- so the safer Go story is now:
  - Go has at least two positive slices
  - but those slices do not yet show one uniform causal path
  - Go still needs replication before we claim stable language-level effectiveness

## Supported / Inferred / Unverified

### Supported by evidence

- Rust is not representative of all languages.
- Python and Go now reach real method-level failures rather than infrastructure failures.
- Python now has direct evidence that operator correctness changes outcome, not just failure composition.
- Go now has both:
  - a negative same-slice rerun (`v2`) showing the old prompt path was unstable
  - a positive same-slice rerun (`v3`) showing the new public-surface guidance can recover the slice in one attempt
- Python `signature/API-shape recovery` changed the prompt trajectory enough to eliminate the earlier Python syntax/type churn on this slice.

### Reasonable inference

- The most promising cross-language method candidate is still **public API grounding / API-shape recovery**, but it now needs to be paired with language-specific operator maturity.
- The common failure family across Python and Go is currently closer to:
  - using the wrong public surface
  - assuming nonexistent attributes/methods
  - misunderstanding how exceptions/results are surfaced by the framework
  than to raw “coverage can’t be reached”.
- The recovery loop abstraction may be unified, but the dominant *effective* layer differs:
  - Python already benefits from tool-side operator absorption
  - Go currently benefits mostly from prompt-level public-surface grounding on this slice

### Still needs validation

- Whether public-API grounding improves Python outcomes, not just Python failure composition.
- Whether Go needs its own lightweight operator family for:
  - exported-surface misuse
  - unused-binding cleanup
  - invalid assumptions about observable outputs
- Whether those Go operators materially help beyond the prompt improvements, since `v3` succeeded without firing any tool repair.
- Whether multi-language gains remain once we move from single-slice smoke tests to small multi-seed slices.

## Submitability Audit

### novelty audit

- “multi-language” alone is still weak.
- A stronger thesis is:
  - lightweight multi-language test generation becomes practical when the system learns to recover from language- and framework-specific API-shape failures, not only from missing-coverage hints.

### methodology audit

- The methodology is improving because we now have:
  - language-specific targeted reruns
  - traceable failure categories
  - cross-language one-segment comparisons under the same orchestration loop
- We also now know that trace-derived terminal outcomes matter more than summary counters once repair becomes multi-step.

### evaluation audit

- Current evidence is still smoke-level.
- We now have enough to justify a multi-language small-slice evaluation:
  - Rust hard slice
  - Python framework slice
  - Go standard-library-facing slice

### writing audit

- We should stop narrating the project as “Rust recovery + extra languages”.
- The cleaner story is:
  - multi-language support exposes different dominant failure layers;
  - Rust emphasizes compatibility/import/API shape;
  - Python emphasizes framework/public exception shape;
- Go currently exposes a gap between prompt-level public-API reasoning and operator-level recovery support.
- More precisely:
  - Python currently provides the stronger evidence for bounded repair
  - Go currently provides stronger evidence for prompt-level public-surface guidance

### Go (`cobra`) Follow-Up: Harder Slice `DebugFlags`

To test whether the newer Go prompt/operators help on a harder public-surface slice, `DebugFlags` was rerun again with the current instrumentation and guidance.

- workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run2-1774445996`
- trace:
  - `/tmp/cobra-debugflags-v2.jsonl`
- log:
  - `/tmp/cobra-debugflags-v2.log`

Facts:

- dry-run still selected the intended segment:
  - `/tmp/coveragent-crosslang/cobra-debug-run2-1774445996/command.go:1463-1499`
- coverage stayed flat:
  - `91.2% -> 91.2%`
- summary counters:
  - `F=3, G=0, U=0`
- trace sequence:
  - `attempt 1: F(assertion), repair_passes=0`
  - `attempt 2: F(assertion), repair_passes=0`
  - `attempt 3: F(assertion), repair_passes=0`

Observed failure content:

- the model stayed on exported/public APIs:
  - `SetOut` / `SetErr`
  - `Flags()` / `PersistentFlags()`
  - `AddCommand(...)`
- but it repeatedly made semantic mistakes about what must be true for nested output to appear.
- the final failure was no longer about invalid field/method access; instead it was a wrong behavioral assumption:
  - the generated test expected `child` / `grandchild` names in output even though those subcommands did not satisfy the flag-related preconditions that trigger those prints.

Interpretation:

- this slice strengthens the emerging cross-language story:
  - Go is not currently blocked by basic public-surface misuse on this slice
  - Go is currently stalling one layer later, at semantic precondition/oracle reasoning
- bounded repair remained dormant here:
  - no tool repair fired
  - no fixpoint pass was used
- so the next useful Go method is unlikely to be “more compile repair”.
- a more promising direction is:
  - better grounding of behavioral preconditions for recursive/nested structures
  - or weaker, more semantics-aware output oracles for formatted CLI output

### Go (`cobra`) Follow-Up: Recursive Precondition Grounding

After the failed `DebugFlags` rerun above, the Go prompt was extended with a more semantic hint:

- if a recursive walk prints child data only when each child also satisfies inner guards such as `HasFlags()` / `HasPersistentFlags()`, the child fixtures must satisfy those guards too.

Then the same `DebugFlags` slice was rerun again:

- workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run3-1774446331`
- trace:
  - `/tmp/cobra-debugflags-v3.jsonl`
- log:
  - `/tmp/cobra-debugflags-v3.log`

Facts:

- coverage still stayed flat:
  - `91.2% -> 91.2%`
- summary counters:
  - `F=3, G=0, U=0`
- trace sequence stayed:
  - `attempt 1: F(assertion), repair_passes=0`
  - `attempt 2: F(assertion), repair_passes=0`
  - `attempt 3: F(assertion), repair_passes=0`

But the failure trajectory changed materially:

- attempt 1:
  - the generated test now gave child and grandchild commands their own flags
  - this is exactly the missing recursive precondition that the previous run had failed to satisfy
- attempt 2:
  - the model started reasoning about output-writer inheritance via `SetOut`, `OutOrStderr`, and `getOut`
- attempt 3:
  - the generated oracle correctly switched from `<string>` to the actual rendered default value `default`
  - the remaining failure narrowed to brittle output formatting expectations:
    - the test still over-constrained blank lines / exact line count in recursive output

Interpretation:

- this is a meaningful methodological improvement even though the slice still ends in `F`:
  - the new hint did not improve coverage
  - but it did move the model to a strictly deeper semantic layer
- more precisely, the dominant Go failure stack on this harder slice now looks like:
  - public-surface grounding: mostly solved
  - recursive precondition grounding: partially solved
  - writer/output inheritance understanding: partially solved
  - output oracle robustness: still unsolved

Implication for the paper:

- the multi-language story should not stop at “public API grounding”.
- on Go, the next stronger method candidate is:
  - `behavioral precondition grounding` for nested structures
  - plus `oracle normalization` for formatted CLI output

### Go (`cobra`) Follow-Up: Positive Recovery Without Tool Repair

Before the new Go assertion operator was live-validated, the same `DebugFlags` slice was rerun once more under the improved prompt stack:

- workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run4-1774447466`
- trace:
  - `/tmp/cobra-debugflags-v4.jsonl`
- log:
  - `/tmp/cobra-debugflags-v4.log`
- saved test:
  - `/tmp/coveragent-crosslang/cobra-debug-run4-1774447466/coverup_001_test.go`

Facts:

- trace sequence:
  - `attempt 1: F(assertion), repair_passes=0`
  - `attempt 2: G, repair_passes=0`
- final result:
  - coverage improved to a full hit on the target segment
  - saved test covered all target lines and branches in `DebugFlags`

Interpretation:

- this is an important positive result for the paper:
  - the harder Go slice is recoverable
  - the recovery can happen after the model is pushed through the deeper semantic layers identified above
- but the causal boundary is still clear:
  - this was **not** a tool-repair win
  - the recovery still came from prompt-guided LLM retry

### Go (`cobra`) Follow-Up: Assertion Operator Still Not Taking Over

After registering a new Go assertion fixer for brittle formatted-output oracles in [`repair.py`](/home/zzzccc/coverup/src/coverup/agents/repair.py), the same slice was rerun again:

- workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run5-1774447774`
- trace:
  - `/tmp/cobra-debugflags-v5.jsonl`
- log:
  - `/tmp/cobra-debugflags-v5.log`

Facts:

- trace sequence:
  - `attempt 1: F(assertion), repair_passes=0`
  - `attempt 2: F(assertion), repair_passes=0`
- `tool_fixes=[]` throughout
- the remaining failures were still exactly in the brittle output-oracle family:
  - blank-line / line-count mismatches
  - exact line equality mismatches on formatted flag output

Interpretation:

- this is a negative but useful result:
  - the new operator family is directionally aligned with the right failure layer
  - but its current pattern coverage is still too narrow to intercept the real generated-test shapes on this slice
- so the stronger claim today is:
  - Go now has good evidence for `behavioral precondition grounding`
  - Go does **not yet** have good evidence for bounded assertion-layer repair

### Go (`cobra`) Follow-Up: Repair Layer Begins To Take Over

After widening the Go assertion operator to match the real `DebugFlags` failures seen in `v6` and `v7`, the same slice was rerun twice more:

- `v8` workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run8-1774448759`
- `v8` trace:
  - `/tmp/cobra-debugflags-v8.jsonl`
- `v8` log:
  - `/tmp/cobra-debugflags-v8.log`
- `v9` workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run9-1774448969`
- `v9` trace:
  - `/tmp/cobra-debugflags-v9.jsonl`
- `v9` log:
  - `/tmp/cobra-debugflags-v9.log`

Facts:

- `v8` no longer stayed on plain `llm` retries:
  - attempt 1: `tool_repair+llm`, `repair_passes=1`
  - attempt 2: `tool_repair+llm`, `repair_passes=1`
- `v9` also stayed on `tool_repair+llm` for both attempts:
  - attempt 1: `tool_repair+llm`, `repair_passes=1`
  - attempt 2: `tool_repair+llm`, `repair_passes=1`
- so the recovery layer is now genuinely engaged on this harder Go slice.
- coverage stayed flat in both runs:
  - `91.2% -> 91.2%`
- summary counters stayed:
  - `F=2, G=0, U=0`

More detailed failure evolution:

- `v7` showed the first post-prompt brittle-oracle family:
  - `expected output not found: ...`
  - expected strings over-specified whole lines such as shorthand/value combinations that were not semantically stable
- after adding canonicalization for those expected strings, `v8` moved to a different family:
  - exact line equality mismatches on whitespace / marker details
  - `expected N lines of output, got M` on recursive cases
- after broadening the operator again, `v9` still entered `tool_repair+llm`, but the repair set changed:
  - `go_add_nonempty_output_helper`
  - `go_add_line_normalizer`
  - `go_add_normalized_contains_helper`
  - `go_normalize_contains_output_asserts`

Interpretation:

- this is the first solid evidence that Go is no longer in the “repair is dormant” state:
  - bounded repair still does not produce a `G`
  - but it now **stably intercepts** the assertion-layer failure before the next LLM retry
- that changes the research judgment in an important way:
  - earlier Go evidence mainly supported prompt-level semantic grounding
  - current Go evidence now supports a stronger systems claim:
    - the same recovery loop that worked more clearly in Python can also begin to absorb Go assertion failures
    - but Go operator maturity is still behind Python operator maturity

What remains unsolved:

- the Go operator still under-models two real failure families on `DebugFlags`:
  - recursive-output line-count expectations
  - semantic marker expectations such as `[LP]` vs `[P]`
- so the strongest safe claim is now:
  - Go has **repair-assisted recovery activity**
  - Go does **not yet** have stable repair-assisted outcome gains

### Go (`cobra`) Follow-Up: Executability Gate Cleared and First Repair-Assisted Win

Two more reruns pushed the same `DebugFlags` slice into a more publication-relevant state:

- `v10` workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run10-1774449435`
- `v10` trace:
  - `/tmp/cobra-debugflags-v10.jsonl`
- `v10` log:
  - `/tmp/cobra-debugflags-v10.log`
- `v11` workspace:
  - `/tmp/coveragent-crosslang/cobra-debug-run11-1774449992`
- `v11` trace:
  - `/tmp/cobra-debugflags-v11.jsonl`
- `v11` log:
  - `/tmp/cobra-debugflags-v11.log`

Facts:

- `v10` exposed a new executability gate rather than a new semantic failure:
  - attempt 1 entered `tool_repair+llm`
  - repair fixes were applied
  - but the repaired test then tripped the backend guard:
    - `[coverup] generated test has 403 lines / 12225 chars, which exceeds the limit (400 lines / 20000 chars).`
- this motivated a small Go backend change:
  - size-aware compaction now strips comment-only lines and repeated blank lines before enforcing the test-size cap
  - code location:
    - `src/coverup/languages/go_backend.py`
- `v11` then produced the first real positive `DebugFlags` result:
  - terminal trace:
    - attempt 1: `tool_repair+llm`, `repair_passes=1`, outcome `G`
  - repair set:
    - `go_add_nonempty_output_helper`
    - `go_add_line_normalizer`
    - `go_add_normalized_contains_helper`
    - `go_add_debugflag_expectation_canonicalizer`
    - `go_normalize_actual_output_lines`
    - `go_normalize_expected_output_lines`
    - `go_iterate_normalized_expected_output`
    - `go_drop_position_sensitive_contains_asserts`
  - coverage improved:
    - `91.2% -> 92.0%`
  - gained target coverage included the whole targeted `DebugFlags` region
  - the log explicitly says:
    - `[REPAIR] Tool repair succeeded after pass 1 — skipping LLM error prompt`

Interpretation:

- this is the first solid evidence that Go has crossed from:
  - `repair-assisted activity`
  - to `repair-assisted benefit`
- it also strengthens the method judgment:
  - the next real bottleneck after prompt-level grounding can be an executability gate such as test-size blow-up
  - bounded repair plus lightweight executability control can matter even before another LLM correction round
- the stronger safe claim is now:
  - Go has one real positive slice showing repair-assisted outcome lift
  - Go still does **not yet** have stable multi-slice evidence comparable to Python

Residual risks:

- `v11` is still one slice on one project
- the summary JSON reports `F=1, G=1`, but the trace has only one terminal `G`
- so trace-derived terminal outcomes remain the only safe evaluation basis

### Go (`cobra`) Medium Slice: `InitDefaultHelpCmd` Exposes Exit-Path Semantics

To test whether the Go story extends beyond `ResetFlags` and `DebugFlags`, a medium-difficulty slice was added:

- target:
  - `command.go:1232-1277`
  - function: `InitDefaultHelpCmd`

Artifacts:

- `v1` trace:
  - `/tmp/cobra-inithelp-v1.jsonl`
- `v1` log:
  - `/tmp/cobra-inithelp-v1.log`
- `v2` trace:
  - `/tmp/cobra-inithelp-v2.jsonl`
- `v2` log:
  - `/tmp/cobra-inithelp-v2.log`
- `v3` trace:
  - `/tmp/cobra-inithelp-v3.jsonl`
- `v3` log:
  - `/tmp/cobra-inithelp-v3.log`
- `v4` trace:
  - `/tmp/cobra-inithelp-v4.jsonl`
- `v4` log:
  - `/tmp/cobra-inithelp-v4.log`
- `v5` trace:
  - `/tmp/cobra-inithelp-v5.jsonl`
- `v5` log:
  - `/tmp/cobra-inithelp-v5.log`
- `v6` trace:
  - `/tmp/cobra-inithelp-v6.jsonl`
- `v6` log:
  - `/tmp/cobra-inithelp-v6.log`
- `v7` trace:
  - `/tmp/cobra-inithelp-v7.jsonl`
- `v7` log:
  - `/tmp/cobra-inithelp-v7.log`
- `v8` trace:
  - `/tmp/cobra-inithelp-v8.jsonl`
- `v8` log:
  - `/tmp/cobra-inithelp-v8.log`

Failure evolution:

- `v1` exposed the first wrong strategy:
  - illegal package-function mocking:
    - `cannot assign to CheckErr`
- `v2` moved away from direct monkeypatching, but replaced it with another wrong strategy:
  - writing and building a standalone temp Go program outside the module
  - this failed with module-resolution errors:
    - `go.mod file not found`
    - `no required module provides package github.com/spf13/cobra`
- `v3` showed the next recovery step:
  - no more `CheckErr = ...`
  - no more temp-module build
  - but the test still assumed:
    - `CheckErr(c.Root().Usage())` must exit with code `1`
    - `Unknown help topic` should be observed on stderr
- source inspection then clarified the actual semantics:
  - `CheckErr` only exits when its argument is non-nil
  - `Usage()` and `Help()` often print and return `nil`
  - `c.Printf(...)` writes through the command output writer rather than inherently stderr
- `v4` confirmed that the new guidance changed the model again:
  - it now used the proper in-module helper-process pattern:
    - `os.Args[0]`
    - `-test.run=...`
    - env-var guard
  - it also captured command output via a buffer
  - but it still expected exit code `1`, and the parent observed empty `CombinedOutput()` because child-local buffer contents were never forwarded
- `v5` produced the strongest shift so far:
  - the wrong `exit code 1` oracle disappeared from the first attempt
  - remaining failures became narrower:
    - completion semantics were still slightly misunderstood
    - output-format expectations now mismatched on `%#q` rendering:
      - expected `["nonexistent"]`
      - actual ``[`nonexistent`]``
- `v6` preserved the `repair-engaged negative` recovery class but moved the frontier again:
  - the old `%#q` mismatch stopped being the dominant failure
  - the slice instead failed on:
    - expecting nil completions where `Find(args)` still returned suggestions
    - helper-process output capture that no longer said `no tests to run`, but still produced empty output
    - incorrect reinitialization expectations for `helpCommand`
- source inspection then clarified an even deeper point:
  - `Find(args)` strips flags first
  - the `e != nil` branch is driven primarily by `Args` validation on the matched command
  - unknown topics or raw flag typos alone often do not trigger the `return nil` path
- `v7` confirmed that the new guidance changed the live trajectory again:
  - `testing: warning: no tests to run` disappeared
  - the reinitialization misunderstanding disappeared
  - failures narrowed to:
    - wrong assumptions about how to trigger the `Find(args)` error branch
    - wrong assumptions about where helper-process output should appear
- `v8` pushed the slice into the clearest source-level interpretation so far:
  - the model explicitly looked up `PositionalArgs` and `NoArgs`
  - the first generated test correctly used `Args: NoArgs` with extra positional args to target the `Find(args)` error branch
  - the first attempt still failed at compile time because it reintroduced `CheckErr` monkeypatching
  - after that compile failure, the second attempt stayed negative but moved to a deeper semantic frontier:
    - root-completion cardinality was still mis-modeled (`expected 1 completions, got 2`)
    - the helper-process path still expected an exit when the observed run succeeded with empty stderr/stdout
  - trace-wise, `v8` is still `tool_repair+llm/F x2`, but its first attempt is now classified as `unknown` rather than immediate `assertion`, and the only tool repair that fired was cleanup of newly introduced unused bindings

Interpretation:

- this slice exposes a distinct Go failure family that is deeper than API-shape or compile-layer mistakes:
  - `Find(args)` / `Args`-validator semantics
  - help-command/root completion cardinality
  - helper-process exit-path semantics
  - writer-channel semantics
  - formatted-output oracle brittleness
- this is not yet a positive Go slice
- but it is already valuable evidence for the paper because the recovery trajectory moved in the expected direction:
  - illegal monkeypatching
  - wrong standalone temp build
  - wrong exit/stderr oracle
  - helper-process/output semantics
  - narrower output-format oracle mismatch
  - source-level `Find(args)` / `NoArgs` reasoning
  - deeper but still unresolved helper-process exit/output assumptions

## Best Next Step

- Next method to try:
  - keep **public API grounding** as a shared prompt layer
  - keep the new Go assertion operators and the new size-aware executability control
  - test whether the `DebugFlags` win reproduces on:
    - one more hard slice in `cobra`
    - one simpler exported-API slice
  - only after that decide whether Go belongs in the main effectiveness section or the mechanism section
- Next experiments to run:
  - Python: move from slice-level reruns to trace-based aggregation over a small slice set
  - Go: treat `DebugFlags` as the first positive non-Python slice, then immediately test one more Go slice for replication
  - Rust: keep Rust as the hard language slice, not the only evidence source
