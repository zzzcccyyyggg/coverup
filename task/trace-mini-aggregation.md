# Trace Mini Aggregation

Date: 2026-03-25

## Core Judgment

The current paper should evaluate the **recovery loop itself** rather than only final coverage.

Even with the small slice set we already have, trace-derived outcomes reveal a pattern that plain coverage would hide:

- some slices recover through **tool_repair+llm**
- some recover through **prompt-first llm**
- some show **repair engagement without outcome lift**

That difference is already central to the paper's method claim.

## Current Slice Table

| Slice | Trace | Attempts | Terminal | Actions | Avg repair passes | Tool fixes fired | Interpretation |
| --- | --- | ---: | --- | --- | ---: | --- | --- |
| Python `click` `v18` | `/tmp/click-full-python-seg-v18.jsonl` | 2 | `G` | `tool_repair+llm`, `tool_repair+llm` | 1.5 | yes | strongest Python repair-assisted positive case |
| Go `DebugFlags` `v11` | `/tmp/cobra-debugflags-v11.jsonl` | 1 | `G` | `tool_repair+llm` | 1.0 | yes | first non-Python repair-assisted positive case |
| Go `ResetFlags` `v6` | `/tmp/cobra-resetflags-v6.jsonl` | 1 | `G` | `llm` | 0.0 | no | positive Go case, but prompt-first |
| Go `ResetFlags` `v4` | `/tmp/cobra-resetflags-v4.jsonl` | 3 | `F` | `tool_repair+llm` x3 | 0.33 | yes | repair engaged, but family incomplete |

## Supported Facts

- The same orchestration loop can produce **different recovery modes** even within one language.
- Python currently has the clearest repair-assisted evidence.
- Go now has:
  - one repair-assisted positive case (`DebugFlags`)
  - one prompt-first positive case (`ResetFlags v6`)
  - one repair-engaged negative case (`ResetFlags v4`)
- Therefore the Go story is no longer "works" vs "doesn't work".
- The real Go story is that **recovery path type varies by slice and operator maturity**.

## Why This Matters For The Paper

This table already supports three writing decisions:

1. The paper should not treat all `G` outcomes as equivalent.
2. The paper should distinguish:
   - prompt-first recovery
   - repair-assisted recovery
   - repair-engaged but unsuccessful recovery
3. Trace-derived evaluation is not optional bookkeeping; it is necessary to explain *how* the system improves.

## What Is Still Missing

- one more Go slice, ideally medium difficulty, to tell whether the `DebugFlags` repair-assisted path generalizes
- a similar compact table for 2-3 Python slices rather than one strongest positive case
- final aggregation scripts that compute this automatically from trace logs

## Medium-Slice Probe

`InitDefaultHelpCmd` is now the most informative incomplete Go probe:

- `v1`
  - trace: `/tmp/cobra-inithelp-v1.jsonl`
  - observed path: `tool_repair+llm` x3, terminal `F`
  - value: exposed illegal `CheckErr` monkeypatching
- `v3`
  - trace: `/tmp/cobra-inithelp-v3.jsonl`
  - observed path before interruption:
    - attempt 1: `tool_repair+llm`, `F`
    - attempt 2: `tool_repair+llm`, `F`
  - value: moved away from monkeypatching and temp-module build into exit/writer semantics
- `v4`
  - trace: `/tmp/cobra-inithelp-v4.jsonl`
  - observed path before interruption:
    - attempt 1: `llm`, `F`
  - value: switched to the proper `os.Args[0]` helper-process pattern
- `v5`
  - trace: `/tmp/cobra-inithelp-v5.jsonl`
  - observed path before interruption:
    - attempt 1: `tool_repair+llm`, `F`
  - value: removed the wrong `exit code 1` assumption and narrowed the failures to output-format / completion semantics

Interpretation:

- this probe is not yet a terminal positive case
- but it is already strong evidence that the Go loop can move across distinct behavioral failure layers even without immediate coverage gain

## Next Update Target

turn `InitDefaultHelpCmd` from a failure-layer probe into either:

- a near-positive recovery case for output/oracle normalization
- or a clearly named Go operator family for helper-process/output-channel semantics
