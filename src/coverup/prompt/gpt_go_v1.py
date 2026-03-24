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
        all_guidance = dynamic_guidance + file_guidance

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
        all_guidance = self._dynamic_go_guidance(segment) + self._file_specific_guidance(filename)
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
