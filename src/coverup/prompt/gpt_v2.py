import re
import typing as T
from .prompter import *
import coverup.codeinfo as codeinfo


class GptV2Prompter(Prompter):
    """Prompter for GPT 4."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def initial_prompt(self, segment: CodeSegment) -> T.List[dict]:
        filename = segment.path.relative_to(self.args.src_base_dir)
        signature_hint = self._signature_shape_guidance(segment)
        public_api_hint = self._public_api_guidance(segment)

        return [
            mk_message(f"""
You are an expert Python test-driven developer.
The code below, extracted from {filename}, does not achieve full coverage:
when tested, {segment.lines_branches_missing_do()} not execute.
Create new pytest test functions that execute all missing lines and branches, always making
sure that each test is correct and indeed improves coverage.
Use the get_info tool function as necessary.
Always send entire Python test scripts when proposing a new test or correcting one you
previously proposed.
Be sure to include assertions in the test that verify any applicable postconditions.
Please also make VERY SURE to clean up after the test, so as to avoid state pollution;
use 'monkeypatch' or 'pytest-mock' if appropriate.
Write as little top-level code as possible, and in particular do not include any top-level code
calling into pytest.main or the test itself.
{signature_hint}
{public_api_hint}
Respond ONLY with the Python code enclosed in backticks, without any explanation.
```python
{segment.get_excerpt()}
```
""")
        ]


    def error_prompt(self, segment: CodeSegment, error: str) -> T.List[dict] | None:
        guidance = self._error_guidance(segment, error)
        guidance_text = f"\nTargeted recovery hints:\n{guidance}\n" if guidance else ""
        return [mk_message(f"""\
Executing the test yields an error, shown below.
Modify or rewrite the test to correct it; respond only with the complete Python code in backticks.
Use the get_info tool function as necessary.
{guidance_text}

{error}""")
        ]


    def missing_coverage_prompt(self, segment: CodeSegment,
                                missing_lines: set, missing_branches: set) -> T.List[dict] | None:
        return [mk_message(f"""\
The tests still lack coverage: {lines_branches_do(missing_lines, set(), missing_branches)} not execute.
Modify it to correct that; respond only with the complete Python code in backticks.
Use the get_info tool function as necessary.
""")
        ]


    def get_info(self, ctx: CodeSegment, name: str) -> str:
        """
        {
            "name": "get_info",
            "description": "Returns information about a symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "class, function or method name, as in 'f' for function f or 'C.foo' for method foo in class C."
                    }
                },
                "required": ["name"]
            }
        }
        """

        if info := codeinfo.get_info(codeinfo.parse_file(ctx.path), name, line=ctx.begin):
            return "\"...\" below indicates omitted code.\n\n" + info

        return f"Unable to obtain information on {name}."


    def get_functions(self) -> T.List[T.Callable]:
        return [self.get_info]

    def _signature_shape_guidance(self, segment: CodeSegment) -> str:
        try:
            seg_text = segment.get_excerpt()
        except OSError:
            return ""

        hints: list[str] = [
            "Before guessing a call shape, use `get_info` to verify the target function/decorator signature."
        ]
        if re.search(r"def\s+\w+\([^)]*\*\w+", seg_text):
            hints.append(
                "If a callable collects extra positional arguments with `*args`, keep those arguments positional; "
                "in Python, positional arguments must appear before keyword arguments."
            )
            hints.append(
                "Valid shape example: `f(\"value\", \"extra1\", \"extra2\", kw=...)` or `f(first=\"value\", kw=...)`; "
                "invalid shape example: `f(first=\"value\", \"extra1\")`."
            )

        if len(hints) == 1:
            return hints[0]
        return "\n".join(f"- {hint}" for hint in hints)

    def _public_api_guidance(self, segment: CodeSegment) -> str:
        try:
            seg_text = segment.get_excerpt()
        except OSError:
            seg_text = ""

        hints: list[str] = [
            "Prefer public, documented API surfaces and observable outcomes over framework internals."
        ]

        if "from importlib import metadata" in seg_text:
            hints.append(
                "If the production code imports a module inside a callback/function, patch the real runtime import source "
                "(for example `sys.modules` or the imported module), not an invented attribute on the outer module."
            )

        if "Context" in seg_text or "Parameter" in seg_text:
            hints.append(
                "For wrapper/helper APIs, assert on the returned object's documented fields and exception object instead of assuming failures are printed into stdout."
            )

        if len(hints) == 1:
            return hints[0]
        return "\n".join(f"- {hint}" for hint in hints)

    def _error_guidance(self, segment: CodeSegment, error: str) -> str:
        lower = error.lower()
        hints: list[str] = []

        if "syntaxerror" in lower and "positional argument follows keyword argument" in lower:
            hints.append(
                "Reorder the failing call/decorator so every positional argument appears before any keyword argument."
            )
            hints.append(
                "If the target signature contains `*args`, pass optional flag names positionally instead of after a keyword like `version=`."
            )
            hints.append(
                "Use a concrete valid pattern such as `decorator(\"3.0.0\", \"-v\", \"--version-info\")` rather than `decorator(version=\"3.0.0\", \"-v\", ...)`."
            )

        if "got multiple values for argument" in lower:
            hints.append(
                "Do not pass the same parameter both positionally and by keyword. Re-read the callable signature with `get_info` and choose one convention."
            )

        if "does not have the attribute" in lower and "mock.patch" in lower:
            hints.append(
                "Only patch attributes that actually exist on the target object. If the production code imports inside a callback/function, patch the runtime lookup source instead of inventing a module attribute."
            )

        if "result.output" in lower or ("<result" in lower and "result.exception" in lower):
            hints.append(
                "Do not assume failures are rendered into `result.output`. For runner-style APIs, inspect the documented exception/error field when the command failed."
            )

        if "nonetype' object has no attribute 'packagenotfounderror'" in lower:
            hints.append(
                "Do not replace a module with `None` if the code still needs its exception class. Preserve the real exception type first, or patch the import fallback path via `sys.modules`."
            )

        if "attributeerror" in lower and "does not have the attribute" not in lower:
            hints.append(
                "Treat this as a public-API mismatch: re-check which attributes are actually exported by the framework object before patching or asserting on them."
            )

        if "assertionerror" in lower:
            hints.append(
                "Treat this as a semantic mismatch: recompute expected values or exception behavior from the implementation instead of guessing strings."
            )
            if "result.output" in lower and "version " in lower:
                hints.append(
                    "Ground assertions in the real message template. For Click's default version output, expect `%(prog)s, version %(version)s`; "
                    "do not assume the package name appears unless the custom `message` includes `%(package)s`."
                )
            if "str(result.exception)" in lower and "runtimeerror" in lower:
                hints.append(
                    "Do not expect `str(result.exception)` to contain the exception class name. Assert on the exception type or on the message text instead."
                )

        if not hints:
            fallback = [self._signature_shape_guidance(segment), self._public_api_guidance(segment)]
            return "\n".join(
                hint if hint.startswith("- ") else f"- {hint}"
                for hint in fallback
                if hint
            )

        return "\n".join(f"- {hint}" for hint in hints)
