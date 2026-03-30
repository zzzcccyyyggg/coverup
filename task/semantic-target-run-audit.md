# Semantic Target Run Audit

Date: 2026-03-25

Scope:
- project: `similar`
- targeted segment: `src/utils.rs:150-191`
- command style: one-segment targeted rerun using `--focus-segment ... --max-segments 1`
- model: `deepseek/deepseek-coder`

## Core Judgment

The original connectivity blocker turned out to be the local proxy path, not DeepSeek itself.

After bypassing the proxy, the exact same targeted rerun design succeeded end-to-end. That means this experiment design is now usable for causal, low-cost mechanism validation.

## Facts

Initial runs used the following one-segment command pattern:

```bash
PYTHONPATH=src .venv/bin/python -m coverup \
  --language rust \
  --package-dir /tmp/coveragent-similar-workspace/similar \
  --prompt gpt-rust-v1 \
  --model deepseek/deepseek-coder \
  --focus-segment 'src/utils.rs:150-191' \
  --max-segments 1 \
  --trace-log /tmp/coverup-target-utils*.jsonl \
  --log-file /tmp/coverup-target-utils*.log
```

Observed in the initial two runs:

- initial coverage measured successfully (`81.0%`)
- targeted selection succeeded and chose exactly one segment:
  - `/tmp/coveragent-similar-workspace/similar/src/utils.rs:150-191`
- planner initialized with exactly one arm
- blocker injection succeeded before the first model call
- the initial prompt for the exact target segment was fully assembled and logged
- the run then failed at the first LLM request with:
  - `DeepseekException - Cannot connect to host api.deepseek.com:443 ssl:default [None]`

Relevant log evidence:

- first attempt log: [coverup-target-utils.log](/tmp/coverup-target-utils.log)
- second attempt log: [coverup-target-utils-retry.log](/tmp/coverup-target-utils-retry.log)

The repeated connection error appears at:

- [coverup-target-utils.log:42](/tmp/coverup-target-utils.log#L42)
- [coverup-target-utils-retry.log:42](/tmp/coverup-target-utils-retry.log#L42)

We then diagnosed the path more precisely:

- the shell environment had `HTTP_PROXY` / `HTTPS_PROXY` pointing to `127.0.0.1:7890`
- `curl --noproxy '*' https://api.deepseek.com` returned the expected HTTP response from DeepSeek
- direct TLS handshake to `api.deepseek.com:443` succeeded
- therefore the broken component was the local proxy path, not provider availability

After bypassing the proxy, we reran the same targeted `utils` command with `NO_PROXY=api.deepseek.com` and unset `HTTP_PROXY` / `HTTPS_PROXY`.

Observed in the successful rerun:

- initial coverage: `81.0%`
- final coverage: `83.4%`
- counters: `F=1, G=1, U=0`
- blocker injection remained enabled
- trace written to [coverup-target-utils-noproxy.jsonl](/tmp/coverup-target-utils-noproxy.jsonl)
- log written to [coverup-target-utils-noproxy.log](/tmp/coverup-target-utils-noproxy.log)

## Strong Inferences

- Local targeted rerun logic is functioning correctly.
- Prompt construction is functioning correctly.
- Provider access is functioning correctly when the local proxy is bypassed.
- The earlier failure should not be interpreted as a method failure.

## Not Supported

- No claim that `utils.rs:150-191` specifically validated semantic recovery; this rerun succeeded too quickly and did not need the repeated-failure branch.
- No claim that proxy bypass changes model quality; it only restored the intended connectivity path.

## Submission Audit

### Methodology Audit

- improved
- we now know the exact point of failure in the evidence chain

### Evaluation Audit

- no longer blocked by provider connectivity, provided proxy bypass is used
- this targeted design is now valid for follow-up mechanism experiments

### Writing Audit

- be careful not to conflate:
  - “targeted live reruns work”
  - “semantic recovery helped on this targeted segment”

For `utils.rs:150-191`, only the first statement is supported.

## Most Valuable Next Step

Use the same proxy-bypassed targeted command pattern on a segment that actually exhibits repeated `F/U` stall. `utils.rs:150-191` was useful to validate connectivity and end-to-end execution, but it is no longer the right segment for semantic-recovery validation.
