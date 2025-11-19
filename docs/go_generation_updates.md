# Go Generation & Testing Updates

This document records the changes made during the recent Go support hardening pass.

## Backend Enhancements
- Added deterministic temp-file naming, aggressive cleanup, and gofmt/goimports post-processing in `src/coverup/languages/go_backend.py`.
- Captured formatter output and embedded the generated test source in the run log whenever `go test` fails to ease diagnosis.

## Prompting Improvements
- Extended `src/coverup/prompt/gpt_go_v1.py` with `_extra_guidance` so segment-specific hints (e.g., for `command.go`, `bash_completions.go`, `doc/md_docs.go`, `doc/yaml_docs.go`) are injected into initial, retry, and missing-coverage prompts.

## Cobra Baseline Test Fixes
- `src/cobra/coverup_002_test.go`: Realigned `Command.Traverse` assertions with Cobra’s actual flag parsing behavior.
- `src/cobra/coverup_004_test.go`: Matched bash completion expectations to the helpers and env vars the generators really emit.
- `src/cobra/doc/coverup_001_test.go`: Updated YAML doc checks to mirror the formatter’s snake_case structure and flag placement.

## Verification
- Confirmed `go test ./...` succeeds within `src/cobra`.
- CoverUp runs now surface the generated Go test content and formatter diagnostics when retries are required.
