import re
import typing as T

from .prompter import Prompter, mk_message
from ..utils import lines_branches_do
from ..go_codeinfo import get_info_go


class GoGptV1Prompter(Prompter):
    """Prompter tailored for generating Go tests.

    Compared to the Python prompter (gpt-v2), this version:
    - Exposes a ``get_info`` tool function backed by tree-sitter + ``go doc``.
    - Dynamically detects Go idioms (interfaces, error returns, goroutines,
      context.Context, file/network I/O) and injects targeted guidance.
    - Includes branch coverage information (inferred by go_codeinfo) in prompts.
    """

    def initial_prompt(self, segment) -> T.List[dict]:
        filename = segment.path.relative_to(self.args.src_base_dir)
        missing_desc = lines_branches_do(
            segment.missing_lines, set(), segment.missing_branches
        )

        dynamic_guidance = self._dynamic_go_guidance(segment)
        file_guidance = self._file_specific_guidance(filename)
        public_api_guidance = self._public_api_guidance(segment)
        all_guidance = dynamic_guidance + file_guidance + public_api_guidance

        # Extract the import block from the production file for sub-package hints
        import_hint = self._sub_package_import_hint(segment)
        if import_hint:
            all_guidance.append(import_hint)

        constraint_text = self._constraints()
        if all_guidance:
            constraint_text += "\nAdditional guidance:\n" + "\n".join(all_guidance)

        excerpt, note = self._excerpt_with_limit(segment)
        note_text = f"\n{note}\n" if note else ""

        # Add function/method name hint if available
        func_hint = ""
        if segment.name:
            func_hint = f"\nThe function/method to target is: `{segment.name}` (lines {segment.begin}-{segment.end - 1}).\n"

        return [
            mk_message(
                f"""\
You are an expert Go test-driven developer.
The code below, extracted from {filename}, does not achieve full coverage:
when tested, {missing_desc} not execute.
{func_hint}
Create new Go test functions (in a `_test.go` file) that exercise SPECIFICALLY the missing lines annotated
with line numbers below (e.g. `42:`). Write tests that force execution through those exact code paths,
not just any code in the file.
Use the get_info tool function to look up any types, functions, or interfaces you need to understand.
Always send the entire Go test file when proposing a new test or correcting one you previously proposed.

{constraint_text}

Respond ONLY with the Go code enclosed in ```go backticks, without any explanation.
```go
{excerpt}
```
{note_text}"""
            )
        ]

    def error_prompt(self, segment, error: str) -> T.List[dict] | None:
        filename = segment.path.relative_to(self.args.src_base_dir)
        all_guidance = (
            self._dynamic_go_guidance(segment)
            + self._file_specific_guidance(filename)
            + self._public_api_guidance(segment)
            + self._error_recovery_guidance(error)
        )
        guidance_text = ""
        if all_guidance:
            guidance_text = "\nKeep in mind:\n" + "\n".join(all_guidance) + "\n"

        return [
            mk_message(
                f"""\
Executing the test yields an error, shown below.
Modify or rewrite the test to correct it; respond only with the complete Go test file in ```go backticks.
Use the get_info tool function if you need to understand types or function signatures.

{error}
{guidance_text}"""
            )
        ]

    def missing_coverage_prompt(
        self, segment, missing_lines: set, missing_branches: set
    ) -> T.List[dict] | None:
        desc = lines_branches_do(missing_lines, set(), missing_branches)
        filename = segment.path.relative_to(self.args.src_base_dir)
        all_guidance = self._dynamic_go_guidance(segment) + self._file_specific_guidance(filename)
        guidance_text = ""
        if all_guidance:
            guidance_text = "\nRemember:\n" + "\n".join(all_guidance) + "\n"

        return [
            mk_message(
                f"""\
The tests still lack coverage: {desc} not execute.
Modify the tests to correct that; respond only with the complete Go test file in ```go backticks.
Use the get_info tool function if you need to understand more about the code.
{guidance_text}"""
            )
        ]

    # ----- Tool function: get_info for Go -----

    def get_info(self, ctx, name: str) -> str:
        """
        {
            "name": "get_info",
            "description": "Returns the definition of a Go type, function, method, interface, or constant. Use 'TypeName' for types, 'TypeName.Method' for methods, or 'package.Symbol' for cross-package lookups.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Symbol name: 'FuncName', 'TypeName', 'TypeName.Method', or 'pkg.Symbol'"
                    }
                },
                "required": ["name"]
            }
        }
        """
        result = get_info_go(
            ctx.path,
            name,
            module_root=getattr(self.args, "package_dir", None),
            line=ctx.begin,
        )
        if result:
            return result
        return f"Unable to find information on '{name}'. Try a different spelling or a fully qualified name."

    def get_functions(self) -> T.List[T.Callable]:
        return [self.get_info]

    # ----- Constraint text -----

    @staticmethod
    def _constraints() -> str:
        return """\
Constraints:
- Keep the package clause identical to the production file (never switch to `package main`).
- Include every module you reference in the `import` block; every test file must import `testing`; remove unused imports.
- If the test file is in a sub-package (e.g. `package doc`), you MUST use the fully qualified type name from parent packages (e.g. `cobra.Command` not `Command`). Add the required import (e.g. `"github.com/spf13/cobra"`).
- Do NOT redefine or reimplement existing types, methods, functions, constants, or unexported structs/fields from the production code.
- Only emit test functions plus lightweight helpers with unique names that exist purely to support those tests.
- Call the real exported APIs; do not copy production logic into the test.
- Clean up filesystem or environment changes with `t.Cleanup(func() { ... })` and mark shared helpers with `t.Helper()`.
- Prefer table-driven tests (`tests := []struct { ... }`) for covering multiple cases efficiently.
- Include assertions that verify postconditions; use `t.Errorf` / `t.Fatalf` for clear failure messages.
- When testing methods on a struct, construct the struct properly using its exported constructor or literal initialization.
- Focus your test specifically on the annotated missing lines (marked with line numbers like `42:`). Write tests that force execution through those exact code paths.
- Go forbids unused variables. Every declared variable MUST be used. If you only need to discard a return value, use `_`.
- Do NOT assign to package-level functions (e.g. `CheckErr = ...`); they are not addressable in Go.
- When testing template error paths, use `{{.UnknownField}}` rather than raw `{{` to avoid unrecoverable `unexpected EOF` panics."""

    # ----- Dynamic guidance based on code content -----

    def _dynamic_go_guidance(self, segment) -> list[str]:
        """Analyze the segment source to produce targeted Go-specific hints."""
        try:
            source = segment.path.read_text()
            # Only look at the segment's own lines for more relevance
            lines = source.splitlines()
            seg_text = "\n".join(
                lines[max(0, segment.begin - 1) : segment.end]
            )
        except OSError:
            return []

        hints: list[str] = []

        # Interface detection
        if "interface {" in seg_text or "interface{" in seg_text:
            hints.append(
                "- This code involves interfaces. Use get_info to understand the interface contract, "
                "then create lightweight mock/stub implementations within the test file."
            )

        # Error return paths
        if re.search(r'\berror\b', seg_text) and "return" in seg_text:
            hints.append(
                "- Test both success and error return paths. For error paths, pass invalid/edge-case inputs "
                "and assert the returned error is non-nil (or matches a specific sentinel/type)."
            )

        # Goroutine / channel
        if re.search(r'\bgo\s+\w', seg_text) or "chan " in seg_text or "<-" in seg_text:
            hints.append(
                "- This code uses goroutines/channels. Use sync.WaitGroup or buffered channels "
                "with timeouts (select + time.After) to avoid test hangs."
            )

        # context.Context
        if "context.Context" in seg_text or "ctx context" in seg_text:
            hints.append(
                "- Test context cancellation and timeout paths using context.WithCancel / context.WithTimeout."
            )

        # File system operations
        if re.search(r'os\.(Open|Create|Mkdir|Remove|ReadFile|WriteFile)', seg_text) or "ioutil." in seg_text:
            hints.append(
                "- Use t.TempDir() for filesystem operations to ensure automatic cleanup."
            )

        # HTTP / network
        if "http." in seg_text or "net." in seg_text:
            hints.append(
                "- Use net/http/httptest.NewServer for HTTP testing; avoid real network calls."
            )

        # io.Reader / io.Writer
        if re.search(r'io\.(Reader|Writer|ReadCloser|WriteCloser)', seg_text):
            hints.append(
                "- Use bytes.Buffer or strings.NewReader to provide in-memory io.Reader/Writer implementations."
            )

        if "CheckErr(" in seg_text or "os.Exit(" in seg_text:
            hints.append(
                "- If the target path exits through `CheckErr` or `os.Exit`, do NOT try to reassign that package-level function. Instead, re-exec the current test binary (`os.Args[0]` with `-test.run=...` plus an env-var guard) and assert on exit status plus rendered stderr/stdout."
            )
        if "c.Printf(" in seg_text or "Print(" in seg_text or "Println(" in seg_text:
            hints.append(
                "- Be precise about output channels: command printing helpers like `c.Printf` write through the command output writer (`SetOut` / `OutOrStdout()`), not necessarily stderr."
            )
        if "CheckErr(c.Root().Usage())" in seg_text or "CheckErr(cmd.Help())" in seg_text:
            hints.append(
                "- Do not assume `CheckErr(...)` always exits. If the wrapped call is `Usage()` or `Help()`, first check whether that call normally returns `nil` after printing; in that common case the observable effect is rendered output, not process exit."
            )
            hints.append(
                "- If the wrapped `Usage()`/`Help()` path only prints and returns `nil`, prefer calling the command directly in-process and asserting on the command's captured output buffer; reserve helper-process re-exec for paths that truly invoke `os.Exit`."
            )

        # Mutex / sync primitives
        if "sync.Mutex" in seg_text or "sync.RWMutex" in seg_text:
            hints.append(
                "- When testing code with mutexes, consider concurrent access scenarios "
                "and use the -race flag expectations."
            )

        # Reflect usage
        if "reflect." in seg_text:
            hints.append(
                "- Code uses reflection; ensure test values cover different kinds (struct, pointer, slice, map, etc.)."
            )

        if (
            "HasSubCommands()" in seg_text
            and ("HasFlags()" in seg_text or "HasPersistentFlags()" in seg_text)
            and ("commands" in seg_text or "AddCommand" in seg_text)
        ):
            hints.append(
                "- If the code recursively visits child commands but only prints details when each child also satisfies inner guards like `HasFlags()` or `HasPersistentFlags()`, make sure your child/grandchild fixtures also have their own flags when you expect nested output."
            )

        if (
            "ValidArgsFunction" in seg_text
            or "IsAvailableCommand()" in seg_text
            or 'Unknown help topic %#q' in seg_text
        ):
            hints.append(
                "- For Cobra help/completion behavior, remember that a child command only appears as an available command if it is not hidden/deprecated and is either runnable (`Run`/`RunE` set) or has available subcommands. A bare child with only `Use`/`Short` will often be filtered out."
            )
            hints.append(
                "- If you expect a command to appear in `ValidArgsFunction` completions, give it a trivial `Run`/`RunE` or a runnable subcommand, and set a non-empty `Short` so the completion text is meaningful."
            )
            hints.append(
                "- `fmt.Printf(\"%#q\", args)` in Go renders string slices with Go-syntax quoting (often backticks like ``[`topic`]``), not JSON-style `[\"topic\"]`. Avoid overly literal JSON-like expectations for `Unknown help topic` output."
            )
            hints.append(
                "- In `InitDefaultHelpCmd`, the error-path branch is guarded by `cmd, _, e := c.Root().Find(args)` and only returns nil completions when `e != nil`. `Find(...)` strips flags first and usually falls back to the current/root command for unknown topics, so an unknown topic string or bad flag alone often does **not** trigger that branch."
            )
            hints.append(
                "- To cover the `return nil, ShellCompDirectiveNoFileComp` path, make `Find(args)` return an error through `Args` validation on the matched command (for example `Args: NoArgs` / `ExactArgs(0)` with leftover positional args), rather than assuming unknown topics or raw flag typos will do it."
            )
            hints.append(
                "- If you use the helper-process pattern with `os.Args[0]` and `-test.run=...`, the regex must match the currently executing test function exactly. Re-exec the same test name or a real helper test name; otherwise the child prints `testing: warning: no tests to run` and your output oracle is meaningless."
            )
            hints.append(
                "- `InitDefaultHelpCmd` does **not** rebuild a fresh help command every time. If `c.helpCommand` already exists, it removes and re-adds that same command pointer. Do not expect mutated fields like `Short` to reset to defaults on the second call."
            )

        return hints

    @staticmethod
    def _public_api_guidance(segment) -> list[str]:
        try:
            source = segment.path.read_text()
            lines = source.splitlines()
            seg_text = "\n".join(
                lines[max(0, segment.begin - 1) : segment.end]
            )
        except OSError:
            seg_text = ""

        hints: list[str] = [
            "- Prefer exported/public methods and observable behavior over unexported fields or internal buffers."
        ]

        if "flag.NewFlagSet" in seg_text or "SetOutput" in seg_text or "FlagSet" in seg_text:
            hints.append(
                "- For flag-set behavior, validate exported effects such as `Lookup`, parse errors, or emitted command output instead of inspecting internal storage."
            )
            hints.append(
                "- If a method recreates a flag set (for example by calling `flag.NewFlagSet`), do not assume flags added before that reset still exist afterward; re-register any flags you want to parse after the reset."
            )

        if "Println" in seg_text or "Print" in seg_text or "OutOrStdout" in seg_text:
            hints.append(
                "- When a command reports through printing helpers, capture the command's output writer and assert on the rendered text rather than on internal state."
            )

        return hints

    @staticmethod
    def _error_recovery_guidance(error: str) -> list[str]:
        lower = error.lower()
        hints: list[str] = []

        if "cannot refer to unexported field" in lower or "has no field or method" in lower:
            hints.append(
                "- Do not read or mutate unexported fields directly. Rework the test to drive the behavior through exported methods on the public type."
            )

        if "undefined" in lower and "output" in lower:
            hints.append(
                "- If a helper object has no exported accessor like `Output()`, stop asserting on that accessor and instead verify exported behavior such as lookups, parse results, or command output."
            )

        if "unknown flag:" in lower:
            hints.append(
                "- If parsing fails with `unknown flag`, re-check whether the flag was registered after the state-resetting call you are testing. Do not expect pre-reset flags to survive a fresh `FlagSet`."
            )

        if "declared and not used" in lower:
            hints.append(
                "- Remove unused locals entirely or replace them with `_` bindings; Go compile errors from unused names are not meaningful test assertions."
            )

        if "cannot assign to checkerr" in lower:
            hints.append(
                "- Do not monkeypatch `CheckErr`. Rework the test so the exit path runs by re-executing the current test binary (`os.Args[0]` + `-test.run=...` + env-var guard), then assert on exit code and printed output."
            )

        if "go.mod file not found" in lower or "no required module provides package github.com/spf13/cobra" in lower:
            hints.append(
                "- Do not write and build a standalone Go program in a temp directory. Stay inside the current module and use the helper-process pattern by re-running the current test binary (`os.Args[0]`) instead."
            )

        if "expected exit code 1" in lower and "got error: <nil>" in lower:
            hints.append(
                "- Re-check whether the code under test actually reaches a non-nil argument to `CheckErr`. If the wrapped call is `Usage()` or `Help()`, it often prints and returns `nil`; in that case assert on rendered output instead of expecting process exit."
            )
        if "expected exit code 1" in lower and "got 0" in lower:
            hints.append(
                "- If a helper-process test exits with code 0, the path likely printed successfully without reaching `os.Exit(1)`. Stop expecting exit status 1 unless the wrapped call truly returns a non-nil error."
            )

        if "expected stderr to contain" in lower and "got:" in lower:
            hints.append(
                "- Re-check the output channel. Messages emitted through command printing helpers are often written to the command output writer (`SetOut`) rather than stderr."
            )

        if (
            "expected to find 'sub' in completions, got [help" in lower
            or "expected completions for" in lower
            or "expected completion for" in lower
            or "missing expected completions" in lower
        ):
            hints.append(
                "- Re-check Cobra availability semantics: `ValidArgsFunction` only suggests child commands that are available. Give expected child commands a trivial `Run`/`RunE` or runnable descendants; a child with only `Use`/`Short` is often filtered out while the built-in `help` command remains visible."
            )

        if "expected nil completions for error path" in lower:
            hints.append(
                "- `ValidArgsFunction` only returns `nil` completions on the `Find(args)` error branch. `Find(...)` strips flags and often falls back to the current/root command for unknown topics, so you need an `Args` validation failure on the matched command (for example `Args: NoArgs` / `ExactArgs(0)` plus extra positional args) before expecting `nil`."
            )

        if "expected 'unknown help topic' in output, got:" in lower or "expected 'unknown help topic' in output, got" in lower:
            hints.append(
                "- If you keep the helper-process pattern, remember that a child-local bytes.Buffer is invisible to the parent. Either assert in-process on the buffer directly, or write the captured buffer back to stdout/stderr before the child exits so `CombinedOutput()` can observe it."
            )

        if (
            "expected output to contain \"unknown help topic" in lower
            or "unknown help topic [`" in lower
            or "got \"unknown help topic [`" in lower
        ):
            hints.append(
                "- `Unknown help topic %#q` uses Go-syntax quoting for the `args` slice. Do not expect JSON-style `[\"topic\"]`; either assert on the stable prefix `Unknown help topic` plus key tokens, or match Go's backtick-style rendering."
            )

        if "no tests to run" in lower:
            hints.append(
                "- Your helper-process re-exec did not match a real test name. Make `-test.run=` target the current test function exactly, or branch on an env var inside that same test instead of inventing a nonexistent subprocess test name."
            )

        if "helpcommand should be reinitialized with default short" in lower or (
            "expected short 'help about any command'" in lower and "modified help" in lower
        ):
            hints.append(
                "- `InitDefaultHelpCmd` does not allocate a new help command when one already exists; it removes and re-adds the existing `helpCommand`. Stop expecting `Short` to reset to the default after you mutate the old command. Instead assert that the same help command remains attached and visible in `Commands()`."
            )

        if "not an interface" in lower:
            hints.append(
                "- Do not type-assert a concrete field value. If the field already has a concrete static type, use it directly or avoid asserting on its exact implementation type."
            )

        if "build failed" in lower and not hints:
            hints.append(
                "- Re-check every method or field name with `get_info` before retrying; Go compile failures usually mean the test referenced a non-exported or nonexistent API."
            )

        return hints

    # ----- Sub-package import hint -----

    @staticmethod
    def _sub_package_import_hint(segment) -> str | None:
        """If the test is in a sub-package that imports parent types, remind
        the model to use qualified names (e.g. cobra.Command not Command)."""
        try:
            source = segment.path.read_text()
        except OSError:
            return None

        # Look for import lines to detect cross-package type usage
        imports: list[str] = []
        in_import = False
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ("):
                in_import = True
                continue
            if in_import:
                if stripped == ")":
                    break
                if stripped and not stripped.startswith("//"):
                    imports.append(stripped.strip('"').strip())
            elif stripped.startswith("import "):
                imp = stripped[7:].strip().strip('"')
                imports.append(imp)

        if not imports:
            return None

        # Find imported package aliases used as type prefixes
        prefixes = []
        for imp in imports:
            parts = imp.rsplit("/", 1)
            pkg_name = parts[-1] if parts else imp
            if pkg_name and f"{pkg_name}." in source:
                prefixes.append(f"`{pkg_name}.TypeName` (from `\"{imp}\"`)")

        if prefixes:
            return (
                "- This file imports external packages. In your test, use fully qualified type names like "
                + ", ".join(prefixes[:3])
                + ". Do NOT use bare type names from other packages."
            )
        return None

    # ----- File-specific hints (for known patterns) -----

    @staticmethod
    def _file_specific_guidance(filename) -> list[str]:
        path_str = str(filename)
        hints: list[str] = []

        if path_str.endswith("command.go"):
            hints.append(
                "- When exercising `Command.Traverse`, register flags on the root command using "
                "`PersistentFlags()` and avoid invoking global CLI state like Execute()."
            )
            hints.append(
                "- Avoid touching unexported fields; rely on exported helpers and methods instead."
            )
        if path_str.endswith("bash_completions.go"):
            hints.append(
                "- Focus tests on the string output of helper writers (e.g. buffers) rather than "
                "executing shell registration."
            )
        if "doc/" in path_str and path_str.endswith("md_docs.go"):
            hints.append(
                "- Use temporary buffers to inspect rendered markdown; respect `DisableAutoGenTag`."
            )
        if "doc/" in path_str and path_str.endswith("yaml_docs.go"):
            hints.append(
                "- Inspect the YAML emitted into a buffer and align expectations with the actual formatter."
            )

        return hints

    # ----- Excerpt truncation -----

    @staticmethod
    def _excerpt_with_limit(
        segment, max_lines: int = 200, max_chars: int = 12000
    ) -> T.Tuple[str, str]:
        """Return a possibly truncated excerpt plus a note describing any truncation."""
        raw = segment.get_excerpt()
        note = ""

        lines = raw.splitlines()
        truncated = False

        if len(lines) > max_lines:
            head = max_lines // 2
            tail = max_lines - head
            lines = (
                lines[:head]
                + ["          … (excerpt truncated) …"]
                + lines[-tail:]
            )
            truncated = True

        excerpt = "\n".join(lines)

        if len(excerpt) > max_chars:
            excerpt = (
                excerpt[:max_chars]
                + "\n          … (excerpt truncated for length)"
            )
            truncated = True

        if truncated:
            note = (
                "(Code excerpt truncated to keep the prompt size manageable; "
                "focus on the annotated lines above.)"
            )

        return excerpt, note
