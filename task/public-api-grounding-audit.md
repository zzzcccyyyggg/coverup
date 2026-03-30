# Public API Grounding Audit

Date: 2026-03-25

## Goal

Evaluate whether explicit `public API grounding` guidance is a better multi-language method direction than simply strengthening coverage hints.

## Method Change

- Python:
  - Added public-API and runner/exception-surface guidance to [gpt_v2.py](/home/zzzccc/coverup/src/coverup/prompt/gpt_v2.py)
  - Strengthened mixed positional/keyword signature guidance with valid-vs-invalid shape examples
- Go:
  - Added public-API grounding and error-specific recovery guidance to [gpt_go_v1.py](/home/zzzccc/coverup/src/coverup/prompt/gpt_go_v1.py)

## Experiments

### Python: `click/src/click/decorators.py:420-530`

- Run:
  - trace: `/tmp/click-full-python-seg-v4.jsonl`
  - log: `/tmp/click-full-python-seg-v4.log`
- Outcome:
  - `F=3, G=0, U=0`
  - failure sequence:
    - attempt 1: `syntax`
    - attempt 2: `import`
    - attempt 3: `type`

### Go: `cobra/command.go:1463-1499 (DebugFlags)`

- Run:
  - trace: `/tmp/cobra-debugflags-v1.jsonl`
  - log: `/tmp/cobra-debugflags-v1.log`
- Outcome:
  - `F=3, G=0, U=0`
  - failure sequence:
    - attempt 1: `assertion`
    - attempt 2: `assertion`
    - attempt 3: `assertion`

## Core Findings

### Supported by evidence

- On Go `DebugFlags`, the new guidance successfully pulled the model onto the **observable-output path**:
  - it used `SetOut` / `SetErr`
  - it asserted against rendered text rather than unexported internals
- This is a real methodological improvement over the earlier visibility-heavy failure mode.

- On Python `click`, the new guidance was **not sufficient** to solve the slice.
- It did change the failure shape across retries, but the model still could not stably handle:
  - mixed positional/keyword call shapes for `version_option`
  - import fallback simulation for `importlib_metadata`
  - framework-specific exception/output semantics

### Reasonable inference

- `public API grounding` is promising, but it is **not enough by itself**.
- The better composite method hypothesis is:
  - `signature exemplar grounding` + `public API grounding`

In other words:
- first force the model to use a valid call shape,
- then force it to stay on exported/public surfaces,
- then let coverage guidance optimize for the missing lines.

## Why This Matters for the Paper

### novelty audit

- A stronger claim is emerging:
  - multi-language test generation fails for different reasons, but a shared recovery pattern is still possible if the system first grounds itself in callable signatures and public API surfaces.

### methodology audit

- This experiment improved methodology because it separated:
  - syntax/signature errors
  - visibility/public-API errors
  - semantic/assertion errors

### evaluation audit

- The evidence still does **not** support an effectiveness claim for this new method.
- It **does** support a control-flow / failure-shape claim, especially on Go.

### writing audit

- We should not write:
  - “public API grounding improves coverage.”
- We can write:
  - “public API grounding changes the dominant failure layer and helps move Go generation away from internal-field misuse.”

## Best Next Step

- Implement and test a stronger `signature exemplar grounding` step for Python:
  - when the source signature contains mixed positional and keyword-only arguments, inject an explicit valid/invalid call example and, if possible, an API-specific canonical shape.
- Then rerun the same `click` slice again.
- Keep Go `DebugFlags` as evidence that public-API grounding is directionally useful, even when it does not yet produce `G`.
