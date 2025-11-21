import typing as T

from .prompter import Prompter, mk_message
from ..utils import lines_branches_do


class GoGptV1Prompter(Prompter):
    """Prompter tailored for generating Go tests."""

    def initial_prompt(self, segment) -> T.List[dict]:
        filename = segment.path.relative_to(self.args.src_base_dir)
        path_str = str(filename)
        missing_desc = lines_branches_do(segment.missing_lines, set(), segment.missing_branches)

        extra_guidance = self._extra_guidance(filename)

        constraint_text = """
    Constraints:
    - Keep the package clause identical to the production file (never switch to `package main` or change the name).
    - Include every module you reference in the `import` block; every file must import `testing`, and unused imports must be removed.
    - Do NOT redefine or reimplement existing types, methods, functions, constants, or unexported structs/fields from the production code.
    - Only emit test functions plus lightweight helpers with unique names that exist purely to support those tests.
    - Call the real exported APIs; do not copy production logic, and do not call global entry points like `Execute()` or `cobra.OnInitialize`.
    - Clean up any filesystem or environment changes your test makes (use `t.Cleanup(func() { ... })`) and mark shared helpers with `t.Helper()`.
    - Prefer table-driven tests (`tests := []struct { ... }`) for covering multiple cases efficiently, but keep each test focused on 1-3 closely related tags/branches.
    """

        example_texts = [
            """
    Example of desired output style:
    ```go
    package mypkg

    import (
        "testing"
    )

    func TestCalculate_CoverUp(t *testing.T) {
        tests := []struct{
            name    string
            input   int
            want    int
            wantErr bool
        }{
            {"positive", 10, 20, false},
            {"negative", -1, 0, true},
        }

        for _, tt := range tests {
            t.Run(tt.name, func(t *testing.T) {
                got, err := Calculate(tt.input)
                if (err != nil) != tt.wantErr {
                    t.Errorf("Calculate() error = %v, wantErr %v", err, tt.wantErr)
                    return
                }
                if got != tt.want {
                    t.Errorf("Calculate() = %v, want %v", got, tt.want)
                }
            })
        }
    }
    ```
    """
        ]

        example_text = "\n".join(example_texts)

        if extra_guidance:
            constraint_text += "\nAdditional guidance specific to this file:\n" + extra_guidance

        excerpt, note = self._excerpt_with_limit(segment)
        note_text = f"\n{note}\n" if note else ""

        context_block = f"""Context:
    - File: {filename}
    - Missing coverage: {missing_desc}
    """

        task_block = """Task:
    - Write `_test.go` code that exercises the uncovered paths using Go's `testing` package.
    - Keep the tests hermetic: no network, disk, or global CLI side effects unless guarded by `t.Cleanup`.
    - Prefer clear assertions over logging, and fail fast when expectations are not met.
    """

        excerpt_block = f"""Code excerpt (may be truncated):
    ```go
    {excerpt}
    ```
    """

        return [
            mk_message(
            f"""
    You are an experienced Go engineer writing targeted `_test.go` files.
    {context_block}
    {task_block}
    {constraint_text}
    {example_text}
    Respond only with Go code enclosed in triple backticks (no prose).
    {excerpt_block}
    {note_text}
    """
            )
        ]

    def error_prompt(self, segment, error: str) -> T.List[dict] | None:
        filename = segment.path.relative_to(self.args.src_base_dir)
        extra_guidance = self._extra_guidance(filename)
        guidance_text = ""
        if extra_guidance:
            guidance_text = "\nHints to keep in mind:\n" + extra_guidance + "\n"
        return [
            mk_message(
                f"""
The generated Go tests failed:
{error}
    - Fix the first compiler/runtime error shown above, then ensure the regenerated file builds cleanly.
    - Keep the package clause, imports, helper names, and API usage aligned with the production file (no `package main`, no unused imports, no unexported struct literals).
    - Return a full replacement `_test.go` file enclosed in ```go fences; partial snippets will be discarded.
{guidance_text}
"""
            )
        ]

    def missing_coverage_prompt(self, segment, missing_lines: set, missing_branches: set) -> T.List[dict] | None:
        desc = lines_branches_do(missing_lines, set(), missing_branches)
        filename = segment.path.relative_to(self.args.src_base_dir)
        extra_guidance = self._extra_guidance(filename)
        guidance_text = ""
        if extra_guidance:
            guidance_text = "\nRemember:\n" + extra_guidance + "\n"
        return [
            mk_message(
                f"""
Previous tests compiled but coverage gaps remain: {desc}.
    - Keep the working tests and add/adjust cases until the specific lines/branches above execute while respecting the constraints (correct package, complete imports, unique helpers, no Execute calls).
    - Return the entire updated `_test.go` file inside ```go fences.
{guidance_text}
"""
            )
        ]

    def _extra_guidance(self, filename) -> str:
        path_str = str(filename)
        hints: list[str] = []

        if path_str.endswith("command.go"):
            hints.append(
                "- When exercising `Command.Traverse`, register flags on the root command using `PersistentFlags()` so recursive parsing sees them, and avoid invoking global CLI state like Execute()."
            )
            hints.append(
                "- Avoid touching unexported fields such as `commandCalledAs` or `parentsPflags`; rely on exported helpers and methods instead."
            )

        if path_str.endswith("bash_completions.go"):
            hints.append(
                "- Focus tests on the string output of helper writers (e.g. buffers) rather than executing shell registration, and keep command naming simple so replacements are easy to assert."
            )

        if path_str.endswith("doc/md_docs.go"):
            hints.append(
                "- Use temporary buffers to inspect rendered markdown; prefer verifying substrings and respect `DisableAutoGenTag` behavior without mutating global state."
            )

        if path_str.endswith("doc/yaml_docs.go"):
            hints.append(
                "- Inspect the YAML emitted into a buffer and align expectations with the actual formatter (synopsis lines are single-line unless multi-line input requires a block)."
            )

        return "\n".join(hints)

    def _excerpt_with_limit(self, segment, max_lines: int = 200, max_chars: int = 12000) -> T.Tuple[str, str]:
        """Return a possibly truncated excerpt plus a note describing any truncation."""
        raw = segment.get_excerpt()
        note = ""

        lines = raw.splitlines()
        truncated = False

        if len(lines) > max_lines:
            head = max_lines // 2
            tail = max_lines - head
            lines = lines[:head] + ["          … (excerpt truncated) …"] + lines[-tail:]
            truncated = True

        excerpt = "\n".join(lines)

        if len(excerpt) > max_chars:
            excerpt = excerpt[:max_chars] + "\n          … (excerpt truncated for length)"
            truncated = True

        if truncated:
            note = "(Code excerpt truncated to keep the prompt size manageable; focus on the annotated lines above.)"

        return excerpt, note
