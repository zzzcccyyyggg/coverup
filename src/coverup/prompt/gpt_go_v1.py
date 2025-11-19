import typing as T

from .prompter import Prompter, mk_message
from ..utils import lines_branches_do


class GoGptV1Prompter(Prompter):
    """Prompter tailored for generating Go tests."""

    def initial_prompt(self, segment) -> T.List[dict]:
        filename = segment.path.relative_to(self.args.src_base_dir)
        missing_desc = lines_branches_do(segment.missing_lines, set(), segment.missing_branches)

        extra_guidance = self._extra_guidance(filename)

        constraint_text = """
    Constraints:
    - Keep the package clause identical to the production file (never switch to `package main` or change the name).
    - Include every module you reference in the `import` block; every file must import `testing`, and unused imports must be removed.
    - Do NOT redefine or reimplement existing types, methods, functions, constants, or unexported structs/fields from the production code.
    - Only emit test functions plus lightweight helpers with unique names that exist purely to support those tests.
    - Call the real exported APIs; do not copy production logic, and do not call global entry points like `Execute()` or `cobra.OnInitialize`.
    - Clean up any filesystem or environment changes your test makes.
    """

        if extra_guidance:
            constraint_text += "\nAdditional guidance specific to this file:\n" + extra_guidance

        return [
            mk_message(
                f"""
You are an experienced Go engineer writing targeted `_test.go` files.
The following Go code, taken from {filename}, lacks coverage: {missing_desc}.
Write Go unit tests that execute the missing lines, using the standard `testing` package.
Ensure tests compile without external dependencies, include assertions, and clean up any filesystem or environment state.
{constraint_text}
Respond only with Go code enclosed in triple backticks.
```go
{segment.get_excerpt()}
```
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
    Focus on the first compiler/runtime error, fix it, and regenerate a complete test file.
    Make sure the package name, imports, helper names, and use of exported APIs follow the constraints (no unexported struct literals, no missing imports, no `package main`).
    Respond only with complete Go source enclosed in ```go blocks.
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
    Revise or add Go tests that cover the missing behavior while still following the constraints (correct package, complete imports, only unique helpers, no unexported struct access, no Execute calls). Respond only with complete Go code in ```go fences.
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
