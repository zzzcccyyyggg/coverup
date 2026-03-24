import re
import typing as T

from .prompter import Prompter, mk_message
from ..utils import lines_branches_do
from ..rust_codeinfo import get_info_rust


class RustGptV1Prompter(Prompter):
    """Prompter tailored for generating Rust tests.

    Designed to be analogous to GoGptV1Prompter, adapted for Rust idioms:
    - Exposes a ``get_info`` tool function backed by tree-sitter.
    - Dynamically detects Rust idioms (traits, error handling, async, unsafe,
      lifetimes) and injects targeted guidance.
    - Includes branch coverage information in prompts.
    """

    @property
    def _crate_name(self) -> str:
        """Get the crate name for use in import statements."""
        crate_name = getattr(self.args, '_crate_name', None)
        if not crate_name:
            # Read from Cargo.toml — walk up from package_dir to find it
            import re as _re
            candidate = self.args.package_dir.resolve()
            for _ in range(6):
                cargo_toml = candidate / 'Cargo.toml'
                if cargo_toml.exists():
                    m = _re.search(r'name\s*=\s*"([^"]+)"', cargo_toml.read_text())
                    if m:
                        crate_name = m.group(1).replace('-', '_')
                    break
                parent = candidate.parent
                if parent == candidate:
                    break
                candidate = parent
        if not crate_name:
            crate_name = 'crate'
        return crate_name.replace('-', '_')

    def initial_prompt(self, segment) -> T.List[dict]:
        filename = segment.path.relative_to(self.args.src_base_dir)
        missing_desc = lines_branches_do(
            segment.missing_lines, set(), segment.missing_branches
        )

        dynamic_guidance = self._dynamic_rust_guidance(segment)
        all_guidance = dynamic_guidance

        constraint_text = self._constraints()
        if all_guidance:
            constraint_text += "\nAdditional guidance:\n" + "\n".join(all_guidance)

        excerpt, note = self._excerpt_with_limit(segment)
        note_text = f"\n{note}\n" if note else ""

        # Function/method name hint
        func_hint = ""
        if segment.name:
            func_hint = (
                f"\nThe function/method to target is: `{segment.name}` "
                f"(lines {segment.begin}-{segment.end - 1}).\n"
            )

        return [
            mk_message(
                f"""\
You are an expert Rust test-driven developer.
The code below, extracted from {filename}, does not achieve full coverage:
when tested, {missing_desc} not execute.
{func_hint}
Create new Rust test functions that exercise SPECIFICALLY the missing lines annotated
with line numbers below (e.g. `42:`). Write tests that force execution through those exact code paths,
not just any code in the file.
Use the get_info tool function to look up any types, functions, traits, or structs you need to understand.
Always send the entire Rust test file when proposing a new test or correcting one you previously proposed.

{constraint_text}

Respond ONLY with the Rust code enclosed in ```rust backticks, without any explanation.
```rust
{excerpt}
```
{note_text}"""
            )
        ]

    def error_prompt(self, segment, error: str) -> T.List[dict] | None:
        filename = segment.path.relative_to(self.args.src_base_dir)
        all_guidance = self._dynamic_rust_guidance(segment)
        guidance_text = ""
        if all_guidance:
            guidance_text = "\nKeep in mind:\n" + "\n".join(all_guidance) + "\n"

        return [
            mk_message(
                f"""\
Executing the test yields an error, shown below.
Modify or rewrite the test to correct it; respond only with the complete Rust test file in ```rust backticks.
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
        all_guidance = self._dynamic_rust_guidance(segment)
        guidance_text = ""
        if all_guidance:
            guidance_text = "\nRemember:\n" + "\n".join(all_guidance) + "\n"

        return [
            mk_message(
                f"""\
The tests still lack coverage: {desc} not execute.
Modify the tests to correct that; respond only with the complete Rust test file in ```rust backticks.
Use the get_info tool function if you need to understand more about the code.
{guidance_text}"""
            )
        ]

    # ----- Tool function: get_info for Rust -----

    def get_info(self, ctx, name: str) -> str:
        """
        {
            "name": "get_info",
            "description": "Returns the definition of a Rust type, function, method, trait, enum, or constant. Use 'TypeName' for types, 'TypeName::method' for methods, or 'module::Symbol' for cross-module lookups.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Symbol name: 'func_name', 'TypeName', 'TypeName::method', or 'module::Symbol'"
                    }
                },
                "required": ["name"]
            }
        }
        """
        result = get_info_rust(
            ctx.path,
            name,
            crate_root=getattr(self.args, "package_dir", None),
            line=ctx.begin,
        )
        if result:
            return result
        return f"Unable to find information on '{name}'. Try a different spelling or a fully qualified name."

    def get_functions(self) -> T.List[T.Callable]:
        return [self.get_info]

    # ----- Constraint text -----

    def _constraints(self) -> str:
        cn = self._crate_name
        api_summary = self._crate_api_summary()
        return f"""\
Constraints:
- Write tests as standalone functions annotated with `#[test]`. Do NOT wrap them in a `mod tests {{ }}` block — the test file is compiled as a standalone integration test.
- Always add `use {cn}::*;` or explicit `use {cn}::SomeType;` imports at the top so that production types and functions are in scope. Do NOT use `use super::*;` — that only works for inline test modules.
- NEVER import or reference private (non-pub) structs, functions, or types. Only `pub` items are accessible from integration tests. If the code under test is private, test it INDIRECTLY by calling public API functions that use it internally.
- NEVER import from private sub-modules. For example, if module `foo` is private, `use {cn}::foo::Bar;` will fail with E0432. Check the available import paths below.
- Do NOT redefine or reimplement existing types, methods, functions, constants, or structs/enums from the production code.
- Only emit test functions plus lightweight helpers with unique names that exist purely to support those tests.
- Call the real exported APIs; do not copy production logic into the test.
- Use `assert!`, `assert_eq!`, `assert_ne!` for assertions. Use `#[should_panic]` for expected panics.
- For error paths, use `.unwrap_err()`, `.is_err()`, or the `matches!()` macro to verify error variants.
- Prefer creating test helper structs/mocks within the test module when testing trait implementations.
- Clean up filesystem or environment changes; use `tempfile::TempDir` or `std::env::temp_dir()` for filesystem operations.
- Prefer multiple small test functions over one large test; each test should target a specific code path.
- Include assertions that verify postconditions; use descriptive messages in assert macros.
- Focus your test specifically on the annotated missing lines (marked with line numbers like `42:`). Write tests that force execution through those exact code paths.
- Every variable you declare MUST be used. Use `let _ = expr;` to discard return values.
- Do NOT use `unsafe` blocks unless the production code being tested absolutely requires it.
- When testing generic functions, provide concrete type parameters.
- For `async` functions, use `#[tokio::test]` or block_on depending on the crate's async runtime.
- When testing code that uses `Result`, test both `Ok` and `Err` paths.
- When constructing structs with private fields, use the type's constructor methods or `Default::default()` if available.
- CRITICAL: `use {cn}::*;` ONLY imports items re-exported at the crate root. Items from public sub-modules (like `{cn}::algorithms`, `{cn}::utils`, etc.) must be imported SEPARATELY with their own `use` statement. For example: `use {cn}::utils::diff_slices;` or `use {cn}::utils::*;`.
- Do NOT use both `use {cn}::module_a::*;` and `use {cn}::module_b::*;` if they export items with the same name — this causes E0659 (ambiguity). Use explicit imports instead.
{api_summary}"""

    # ----- Crate public API summary -----

    def _crate_api_summary(self) -> str:
        """Build a concise summary of the crate's public API import paths."""
        api_map = getattr(self.args, '_module_api_map', None)
        if not api_map:
            return ""

        cn = self._crate_name
        lines: list[str] = []
        lines.append("\nAvailable import paths (use ONLY these):")

        # Root-level re-exports
        pub_mods = api_map.get("public_modules", set())
        priv_mods = api_map.get("private_modules", set())

        if priv_mods:
            re_exported = [r for r in api_map.get("root_reexports", []) if "::*" in r]
            if re_exported:
                lines.append(
                    f"- `use {cn}::*;` — imports all public items re-exported at the crate root "
                    f"(from private modules: {', '.join(sorted(priv_mods))})"
                )

        # Public modules
        for mod_name in sorted(pub_mods):
            reexports = api_map.get("submodule_reexports", {}).get(mod_name, [])
            pub_submods = api_map.get("submodule_public_mods", {}).get(mod_name, set())
            pub_items = api_map.get("module_pub_items", {}).get(mod_name, {})
            parts = [f"`use {cn}::{mod_name}::*;`"]
            if reexports:
                items = ", ".join(reexports[:12])
                parts.append(f"(items: {items})")
            elif pub_items:
                all_names = pub_items.get("types", []) + pub_items.get("functions", [])
                if all_names:
                    items = ", ".join(all_names[:12])
                    parts.append(f"(items: {items})")
            lines.append(f"- {' '.join(parts)}")
            if pub_submods:
                for sm in sorted(pub_submods):
                    lines.append(f"  - `use {cn}::{mod_name}::{sm}::*;` — public sub-module")

        if len(lines) <= 1:
            return ""

        return "\n".join(lines)

    # ----- Dynamic guidance based on code content -----

    def _dynamic_rust_guidance(self, segment) -> list[str]:
        """Analyze the segment source to produce targeted Rust-specific hints."""
        try:
            source = segment.path.read_text()
            lines = source.splitlines()
            seg_text = "\n".join(
                lines[max(0, segment.begin - 1): segment.end]
            )
        except OSError:
            return []

        hints: list[str] = []

        # Module import hint — guide to the correct import path for this file
        import_hint = getattr(segment, '_import_hint', None)
        if import_hint:
            hints.append(f"- IMPORT PATH: {import_hint}")

        # Trait detection
        if re.search(r'\btrait\b', seg_text):
            hints.append(
                "- This code involves traits. Use get_info to understand the trait contract, "
                "then create lightweight mock/stub implementations within the test module."
            )

        # impl block detection
        if re.search(r'\bimpl\b', seg_text):
            hints.append(
                "- This code is inside an impl block. Use get_info to look up the type definition "
                "and understand how to construct instances for testing."
            )

        # Result / error handling
        if re.search(r'Result<', seg_text) or "Err(" in seg_text or "?" in seg_text:
            hints.append(
                "- Test both Ok and Err paths. For error paths, pass invalid/edge-case inputs "
                "and assert the returned error using `.unwrap_err()` or `matches!()` macro. "
                "Use `?` operator in test functions that return `Result<(), Box<dyn Error>>`."
            )

        # Option handling
        if "Option<" in seg_text or "None" in seg_text or "Some(" in seg_text:
            hints.append(
                "- Test both Some and None paths for Option types. "
                "Use `.unwrap()` for expected Some, `.is_none()` for expected None."
            )

        # Async code
        if re.search(r'\basync\b', seg_text) or ".await" in seg_text:
            hints.append(
                "- This code uses async. Use `#[tokio::test]` if the crate uses tokio, "
                "or `futures::executor::block_on()` for other async runtimes."
            )

        # Lifetime annotations
        if re.search(r"<'[a-z]", seg_text) or "lifetime" in seg_text.lower():
            hints.append(
                "- This code uses lifetime annotations. Ensure test data outlives "
                "any references; use owned types (String, Vec) where possible in tests."
            )

        # Unsafe code
        if "unsafe" in seg_text:
            hints.append(
                "- This code contains unsafe blocks. Wrap unsafe calls in the test "
                "with proper safety documentation comments."
            )

        # Generic parameters
        if re.search(r'<\s*[A-Z]\w*\s*(?::|,|>)', seg_text):
            hints.append(
                "- This code uses generics. Provide concrete types in your tests "
                "(e.g., use `i32`, `String`, `Vec<u8>` as type arguments)."
            )

        # File system operations
        if re.search(r'std::fs|File::|Path::|PathBuf', seg_text) or "read_to_string" in seg_text:
            hints.append(
                "- Use `tempfile::TempDir` or `std::env::temp_dir()` for filesystem "
                "operations to ensure automatic cleanup."
            )

        # Network / HTTP
        if "TcpListener" in seg_text or "TcpStream" in seg_text or "hyper" in seg_text:
            hints.append(
                "- Use localhost with port 0 for network testing (OS assigns an available port)."
            )

        # Mutex / concurrency
        if re.search(r'Mutex|RwLock|Arc|atomic', seg_text):
            hints.append(
                "- When testing concurrent code, use `Arc` to share data between threads "
                "and `std::thread::spawn` for parallel execution."
            )

        # Derive macros
        if re.search(r'#\[derive\(.*?(Serialize|Deserialize)', seg_text):
            hints.append(
                "- This code uses serde. Test serialization round-trips: "
                "serialize to JSON/string and deserialize back, asserting equality."
            )

        # Pattern matching
        if re.search(r'\bmatch\b', seg_text):
            hints.append(
                "- This code uses pattern matching. Create test cases that exercise "
                "each match arm, including the wildcard/default case if present."
            )

        # Closures
        if re.search(r'\|[^|]*\|', seg_text) and ("fn(" in seg_text or "Fn(" in seg_text or "closure" in seg_text.lower()):
            hints.append(
                "- This code uses closures or function pointers. Provide appropriate "
                "closure arguments in your tests."
            )

        # Private methods – E0624: cannot call private methods from integration tests
        priv_methods = getattr(segment, '_private_methods', None)
        if priv_methods:
            method_set = set(priv_methods)
            names_str = ', '.join(f'`{n}`' for n in priv_methods[:6])
            hints.append(
                f"- IMPORTANT: The method(s) {names_str} are PRIVATE (no `pub`). "
                f"You CANNOT call these methods from integration tests (causes E0624). "
                f"Instead, test them INDIRECTLY by calling PUBLIC methods/functions that "
                f"invoke these private methods internally. Choose inputs that exercise the private code paths."
            )
        else:
            method_set = set()

        # Private types/items – E0603: cannot import private types
        priv_names = getattr(segment, '_private_items', None)
        if priv_names:
            # Filter out method names already warned about above
            type_names = [n for n in priv_names if n not in method_set]
            if type_names:
                names_str = ', '.join(f'`{n}`' for n in type_names[:6])
                cn = self._crate_name
                hints.append(
                    f"- IMPORTANT: The type(s)/item(s) ({names_str}) are PRIVATE (not exported). "
                    f"You CANNOT import or reference them directly (causes E0603). "
                    f"Test them INDIRECTLY by calling public functions from `use {cn}::*;` "
                    f"that use these types internally."
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
