# Python Click Recovery Audit

## Core Judgment

On the targeted Python `click` slice, the current recovery path now has a real, evidenced progression:

- first-order failure: invalid call shape (`syntax`)
- second-order failure: wrong observable expectations (`assertion`)
- final outcome: successful coverage gain (`G`)

This is important for submitability because it shows the system is no longer stuck at "Python prompting is brittle". It now has evidence for a two-stage recovery story:

1. tool-side `call-shape` repair restores executability
2. the loop can then move on to semantic/oracle correction and eventually succeed

## Facts Supported By Data

- Fresh targeted run:
  - workspace: `/tmp/coveragent-crosslang/click-full-run6-1774429163`
  - trace: `/tmp/click-full-python-seg-v8.jsonl`
  - log: `/tmp/click-full-python-seg-v8.log`
- Targeted segment:
  - `/tmp/coveragent-crosslang/click-full-run6-1774429163/src/click/decorators.py:421-524`
- Final result:
  - initial coverage: `89.4%`
  - final coverage: `90.3%`
  - counters: `F=2, G=1, U=0`
  - saved test: `/tmp/coveragent-crosslang/click-full-run6-1774429163/tests/test_coverup_135.py`

Trace progression:

- attempt 1:
  - outcome: `F`
  - category: `syntax`
- attempt 2:
  - outcome: `F`
  - category: `assertion`
- attempt 3:
  - outcome: `G`
  - action: `tool_repair+llm`
  - tool fixes: `["python_reorder_version_option_args"]`
  - `delta_line=0.9756`, `delta_branch=0.95`

Direct log evidence:

- multiline call-shape repair fired:
  - `[REPAIR] Tool-first fixes applied: ['python_reorder_version_option_args']`
- the second-stage failures were semantic/oracle failures rather than import noise:
  - assertions incorrectly expected package names in default output such as `'mypackage' in 'cli, version 2.0.0\\n'`
  - assertions incorrectly expected `str(result.exception)` to include `"RuntimeError"`

## Reasoned Inference

- The Python call-shape guard is no longer hypothetical. It materially changes the recovery path on a real slice.
- The improved Python classifier also matters: the second failure is now labeled `assertion` instead of the earlier misleading `import` label. That is methodologically important because repair and memory are now aligned with the real failure layer.
- The dominant Python challenge on this slice is not framework-private API misuse anymore. It is oracle grounding: understanding what the code actually outputs and what the exception object actually contains.

## High-Risk / Not Yet Supported

- We cannot yet claim that the new `oracle grounding` prompt hints caused the success on this slice.
  - They were added after the successful `v8` run.
- We cannot yet claim a broad Python win.
  - This is still one targeted slice, not a benchmark-level result.
- We should not write that `tool_repair` alone solved the whole problem.
  - It solved the first gate, but success still required later LLM correction.

## Submitability Audit

### Novelty Audit

- "Multi-language" alone still does not carry novelty.
- A stronger novelty direction is emerging:
  - unified recovery loop across languages
  - different dominant failure layers per language
  - Python evidence now supports a layered story: `executability repair -> oracle recovery`

### Methodology Audit

- This is a real improvement.
- We now have causal evidence on Python that a deterministic repair can move the system from syntax failure to semantically meaningful feedback.
- The improved classifier reduces a serious methodology weakness: incorrect error categorization.

### Evaluation Audit

- This result is valid as a targeted case study.
- It is not yet enough as a main quantitative claim.
- The next evaluation step should isolate whether `oracle grounding` reduces attempts or cost on the same slice.

### Writing Audit

- Safe claim:
  - "On Python, tool-side call-shape repair can unblock execution and expose the true oracle-level failure mode."
- Unsafe claim:
  - "Our Python agent is now generally robust."

## Next Best Step

Run one more paired targeted Python experiment on the same slice with the new `oracle grounding` hints enabled, and compare:

- number of failed attempts before first `G`
- whether the second-stage assertion failures shrink
- whether total cost/latency drops relative to `v8`

## Follow-Up Paired Result: v9 Oracle-Grounding Prompt

A paired rerun was executed after adding new Python `oracle grounding` hints to the prompt.

- workspace: `/tmp/coveragent-crosslang/click-full-run7-1774429578`
- trace: `/tmp/click-full-python-seg-v9.jsonl`
- log: `/tmp/click-full-python-seg-v9.log`
- final result:
  - initial coverage: `89.4%`
  - final coverage: `89.4%`
  - counters: `F=3, G=0, U=0`

Trace progression:

- attempt 1:
  - outcome: `F`
  - category: `syntax`
- attempt 2:
  - outcome: `F`
  - category: `visibility`
- attempt 3:
  - outcome: `F`
  - category: `assertion`

Direct evidence:

- tool-side call-shape repair still fired:
  - `[REPAIR] Tool-first fixes applied: ['python_reorder_version_option_args']`
- but the new trajectory no longer converged to `G`
- the second-stage failure moved to public-surface mismatch:
  - `AttributeError: 'Context' object has no attribute 'exited'. Did you mean: 'exit'?`

### Interpretation

- The new prompt changed model behavior, so it is not inert.
- But it is not yet a net win on this slice.
- The current `oracle grounding` wording appears too weakly targeted; instead of correcting the default output / exception-message expectations cleanly, it nudged the model into a different public-API misuse path.

### Updated Risk Assessment

- We cannot claim that the newly added `oracle grounding` prompt improves Python recovery.
- At present, the strongest supported Python result is still `v8`, where:
  - tool-side call-shape repair removed the executability blocker
  - improved classification exposed the real semantic failure layer
  - the loop eventually converged to a successful test

### Updated Next Step

Do not further expand generic Python prompt text first. The better next intervention is likely one of:

- a more targeted deterministic fix for common Click callback/context misuse
- a narrower assertion/oracle repair pass that rewrites only obviously wrong expectations
- or a smaller test-generation target that avoids large multi-test bundles before semantic correction

## Follow-Up System Audit: v10 and v11

Two later targeted reruns clarified that the main improvement is not just "better prompt wording", but a more correct recovery loop.

- `v10` workspace:
  - `/tmp/coveragent-crosslang/click-full-run8-1774430732`
- `v10` trace:
  - `/tmp/click-full-python-seg-v10.jsonl`
- `v10` log:
  - `/tmp/click-full-python-seg-v10.log`

Facts from `v10`:

- trace progression:
  - attempt 1: `F`, `action=tool_repair+llm`, `ir_category=assertion`, `tool_fixes=["python_reorder_version_option_args"]`
  - attempt 2: `F`, `action=tool_repair+llm`, `ir_category=assertion`, `tool_fixes=["python_reorder_version_option_args", "python_reorder_version_option_args"]`
  - attempt 3: `G`, `action=tool_repair+llm`, `delta_line=1.0`, `delta_branch=0.95`
- this matters methodologically because the failed post-repair attempts are now attributed to the *new* error layer (`assertion`) rather than the old pre-repair `syntax` layer

- `v11` workspace:
  - `/tmp/coveragent-crosslang/click-full-run9-1774431044`
- `v11` trace:
  - `/tmp/click-full-python-seg-v11.jsonl`
- `v11` log:
  - `/tmp/click-full-python-seg-v11.log`
- saved test:
  - `/tmp/coveragent-crosslang/click-full-run9-1774431044/tests/test_coverup_135.py`

Facts from `v11`:

- trace progression:
  - attempt 1: `F`, `action=tool_repair+llm`, `ir_category=assertion`, `tool_fixes=["python_fix_click_version_option_oracles"]`
  - attempt 2: `G`, `action=tool_repair+llm`, `delta_line=1.0`, `delta_branch=0.85`
- final result:
  - initial coverage: `89.4%`
  - final coverage: `90.3%`
  - counters: `F=1, G=1, U=0`

Interpretation:

- `v10` shows the recovery loop is now *causally correct*: after tool repair partially succeeds, the LLM sees the new failure surface instead of the stale one.
- `v11` suggests that a narrow deterministic oracle/public-surface operator can reduce the number of failed retries on the same slice.
- This is stronger than a benchmark anecdote. It supports the paper direction that the key abstraction is not "prompt better", but "diagnose failure layer, then apply the smallest operator that matches that layer".

## Follow-Up Stability Audit: v14 Same-Slice Rerun

A same-slice rerun was executed on a clean copy that preserved the old `89.4%` baseline by removing only `test_coverup_135.py`.

- workspace:
  - `/tmp/coveragent-crosslang/click-full-run13-1774431627`
- trace:
  - `/tmp/click-full-python-seg-v14.jsonl`
- log:
  - `/tmp/click-full-python-seg-v14.log`

Final facts:

- attempt 1:
  - `F`
  - `action=tool_repair+llm`
  - `ir_category=assertion`
  - `tool_fixes=["python_reorder_version_option_args"]`
- attempt 2:
  - `F`
  - `action=tool_repair+llm`
  - `ir_category=unknown`
  - `tool_fixes=["python_reorder_version_option_args", "python_reorder_version_option_args"]`
- attempt 3:
  - `G`
  - `action=tool_repair+llm`
  - `ir_category=unknown`
  - `tool_fixes=["python_reorder_version_option_args", "python_reorder_version_option_args", "python_reorder_version_option_args"]`
  - `delta_line=1.0`, `delta_branch=0.95`

Interpretation:

- the first hop was stable: the system again repaired the mixed call shape and moved into a higher-level post-executability failure layer
- the slice still converged to `G`, so the core Python call-shape recovery is more stable than the earlier partial reading suggested
- however, it did *not* reproduce `v11`'s faster `F -> G` convergence
- this means the current operator set is stable enough to recover, but not yet stable enough to recover *efficiently*

What this changed methodologically:

- `v14` exposed a design limitation in the old control flow:
  - each failure only got one layer of tool repair before falling back to the LLM
  - in practice, Python Click often needs a chain like `call-shape -> assertion/oracle`

## Method Update: Bounded Fixpoint Repair

In response, the recovery loop was upgraded from one-shot tool repair to bounded fixpoint repair in [`coverup.py`](/home/zzzccc/coverup/src/coverup/coverup.py#L58) and [`coverup.py`](/home/zzzccc/coverup/src/coverup/coverup.py#L742).

Facts:

- a new constant `MAX_TOOL_REPAIR_PASSES = 3` bounds the repair depth
- after each successful tool-side rewrite, CoverUp now re-runs the test immediately
- if the failure changes, it reclassifies the *new* diagnostic and allows another tool-repair pass before falling back to the LLM

Reasoned inference:

- this is a more paper-worthy direction than adding another Click-specific rule
- it generalizes beyond Python:
  - Rust often needs `import -> type/ownership`
  - Python often needs `executability -> oracle/public surface`
  - Go may need `API shape -> assertion`

Updated submitability judgment:

- safer claim:
  - "Recovery should be modeled as a bounded operator sequence over changing failure layers, not as a single repair step followed by another LLM retry."
- unsafe claim:
  - "The current Python operator set is already stable enough to guarantee two-hop convergence."

## Fixpoint Field Audit: v17 and v18

The recovery loop was instrumented to emit attempt-level `repair_passes` and `fixpoint_exhausted` in the JSONL trace, and the run summary now records whether fixpoint repair was enabled and what the configured pass bound was [coverup.py](/home/zzzccc/coverup/src/coverup/coverup.py#L682) [coverup.py](/home/zzzccc/coverup/src/coverup/coverup.py#L857) [coverup.py](/home/zzzccc/coverup/src/coverup/coverup.py#L1407).

One environment blocker also had to be neutralized for these reruns:

- `pytest_isolate` tried to probe GPUs via `pynvml`, which crashed suite measurement in this shell
- setting `CUDA_VISIBLE_DEVICES=''` avoided that path and restored the old `89.4%` Python baseline

### v17: Negative But Methodologically Useful

- workspace:
  - `/tmp/coveragent-crosslang/click-full-run17-1774435886`
- trace:
  - `/tmp/click-full-python-seg-v17.jsonl`
- log:
  - `/tmp/click-full-python-seg-v17.log`

Facts:

- final coverage stayed at `89.4%`
- summary counters were `F=3, G=0, U=0`
- all three trace entries were terminal `F`
- every failed attempt recorded:
  - `repair_passes=2`
  - `fixpoint_exhausted=true`
  - tool fixes including both `python_reorder_version_option_args` and `python_fix_click_version_option_oracles`
  - terminal category `syntax`

This looked, at first, like a failure of fixpoint repair itself. However, local replay of the deterministic operator sequence against the exact logged assistant output showed that the failure was an implementation bug in the oracle rewrite, not a limitation of the abstraction:

- the regex used `\s*` at end-of-line and accidentally consumed the newline after
  `assert "RuntimeError" in str(result.exception)`
- that merged the next top-level function header into the same line, producing:
  - `assert isinstance(result.exception, RuntimeError)def test_version_option_custom_param_decls():`

This was a real, deterministic operator bug, not an LLM hallucination.

### v18: Bug Fixed, Recovery Restored

- workspace:
  - `/tmp/coveragent-crosslang/click-full-run18-1774436270`
- trace:
  - `/tmp/click-full-python-seg-v18.jsonl`
- log:
  - `/tmp/click-full-python-seg-v18.log`
- saved test:
  - `/tmp/coveragent-crosslang/click-full-run18-1774436270/tests/test_coverup_135.py`

The repair bug was fixed by tightening the line-oriented regexes in [`repair.py`](/home/zzzccc/coverup/src/coverup/agents/repair.py#L608) so they only consume inline spaces and tabs, not newlines.

Facts from `v18`:

- final coverage improved from `89.4%` to `90.3%`
- trace progression:
  - attempt 1:
    - `F`
    - `repair_passes=2`
    - `fixpoint_exhausted=true`
    - tool fixes:
      - `python_reorder_version_option_args`
      - `python_fix_click_version_option_oracles`
      - `python_fix_click_echo_patch_target`
    - terminal category `assertion`
  - attempt 2:
    - `G`
    - `repair_passes=1`
    - `fixpoint_exhausted=false`
    - tool fixes included a final `python_reorder_version_option_args`
    - `delta_line=1.0`, `delta_branch=1.0`

Interpretation:

- this is stronger than "we fixed a Click bug"
- it shows the paper-level mechanism is behaving as intended:
  - one attempt can now absorb multiple failure layers before falling back
  - operator correctness materially changes whether the fixpoint loop surfaces the real downstream failure
  - once the operator sequence is correct, the same slice returns to a positive `G`

### Evaluation Caveat Exposed By Fixpoint

`v18` also exposed an important evaluation detail:

- the summary counters reported `F=2, G=1`
- but the trace only contains one terminal `F` attempt and one terminal `G` attempt

Reason:

- `state.inc_counter('F')` still increments on the initial compile failure inside an attempt, even if that same attempt later succeeds after tool repair

So, after fixpoint repair, the JSON summary counters are no longer equivalent to "terminal attempt outcomes". For publication-grade evaluation:

- paired outcome comparisons should use the trace log as the primary source
- summary counters should be treated as raw internal failure events unless relabeled or revised

Updated submitability judgment:

- safer claim:
  - "Bounded fixpoint repair changes the recovery semantics from one-shot repair to multi-operator absorption, and its effectiveness depends on operator correctness."
- still unsafe claim:
  - "Python fixpoint repair is already benchmark-stable across tasks."

Updated next step:

- adapt offline analysis to derive `terminal F/G/U`, `repair_passes`, and fixpoint exhaustion from trace rather than summary counters
- then rerun one non-Python targeted slice with the same instrumentation to test whether this abstraction generalizes beyond Click
