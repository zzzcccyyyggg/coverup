# Targeted Rerun Audit

Date: 2026-03-25

## Core Judgment

We now have a practical way to convert a vague “rerun the hard slice” idea into a reproducible experiment.

This matters for submitability because the current project no longer fails only at the whole-project level. It now fails on specific hard segments with distinct bottlenecks. Without targeted reruns, we waste runtime and API budget on easy or irrelevant segments and still fail to validate the mechanism we actually changed.

## Code Changes

`coverup.py` now supports lightweight segment targeting:

- `--focus-file`
- `--focus-segment`
- `--focus-name`
- `--max-segments`

These filters operate on the already-generated coverage segments, so they do not change segmentation logic, planner logic, or backend behavior. They only reduce the worklist before execution [coverup.py](/home/zzzccc/coverup/src/coverup/coverup.py#L110) [coverup.py](/home/zzzccc/coverup/src/coverup/coverup.py#L330) [coverup.py](/home/zzzccc/coverup/src/coverup/coverup.py#L1070).

## Verified Fact

The new targeting path was verified with a real CLI dry-run on `similar`:

```bash
PYTHONPATH=src .venv/bin/python -m coverup \
  --language rust \
  --package-dir /tmp/coveragent-similar-workspace/similar \
  --prompt gpt-rust-v1 \
  --model deepseek/deepseek-coder \
  --dry-run \
  --focus-segment 'src/utils.rs:150-191' \
  --max-segments 1
```

Observed result:

- initial coverage measured successfully
- targeted selection printed exactly one segment
- the selected segment was `/tmp/coveragent-similar-workspace/similar/src/utils.rs:150-191`
- planner initialized with exactly one arm
- no model work was performed because `--dry-run` was enabled

## What This Supports

Supported:

- we can now run cheap, reproducible targeted reruns against a specific hard segment
- we can validate semantic-recovery behavior without paying the cost of a full-project run
- we can make future evidence more causal: “this patch changed behavior on this exact segment”

Not supported:

- any performance claim yet
- any claim that targeted reruns improve coverage by themselves

## Why This Matters for the Paper

### Methodology Audit

This is a real methodological improvement.

Before this change, we had to infer too much from long whole-project runs whose early segment mix changed from run to run. That makes reviewer-facing causal claims weak.

After this change, we can validate a mechanism on the exact segment that motivated it.

### Evaluation Audit

This directly improves experimental controllability:

- lower runtime
- lower API cost
- lower variance in early-run segment selection
- clearer attribution between a code change and an observed behavior shift

### Writing Audit

This also improves the narrative discipline of the paper.

Instead of saying “we changed X and the project felt better,” we can say:

1. segment `src/utils.rs:150-191` exhibited repeated semantic panic churn
2. we introduced semantic recovery mode
3. we reran that exact segment with a targeted command
4. then we observed whether the live prompt and failure composition changed

That is much closer to a publishable evidence chain.

## Most Valuable Next Step

Run one targeted real experiment on the exact motivating slice:

```bash
PYTHONPATH=src .venv/bin/python -m coverup \
  --language rust \
  --package-dir /tmp/coveragent-similar-workspace/similar \
  --prompt gpt-rust-v1 \
  --model deepseek/deepseek-coder \
  --trace-log /tmp/semantic-target.jsonl \
  --focus-segment 'src/utils.rs:150-191' \
  --max-segments 1
```

And validate two things only:

1. whether live prompts enter `Semantic recovery mode`
2. whether repeated `panic` churn narrows or turns into a `G`

That is the shortest path from “new mechanism exists” to “new mechanism has usable evidence.”
