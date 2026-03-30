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

    @property
    def _crate_edition(self) -> str:
        """Get the crate edition, defaulting to Cargo's implicit 2015."""
        edition = getattr(self.args, '_crate_edition', None)
        if edition:
            return str(edition)

        candidate = self.args.package_dir.resolve()
        for _ in range(6):
            cargo_toml = candidate / 'Cargo.toml'
            if cargo_toml.exists():
                content = cargo_toml.read_text()
                package_match = re.search(
                    r'^\[package\]\s*(.*?)(?=^\[|\Z)',
                    content,
                    flags=re.MULTILINE | re.DOTALL,
                )
                if not package_match:
                    return "2015"
                edition_match = re.search(
                    r'^\s*edition\s*=\s*"([^"]+)"',
                    package_match.group(1),
                    flags=re.MULTILINE,
                )
                return edition_match.group(1) if edition_match else "2015"
            parent = candidate.parent
            if parent == candidate:
                break
            candidate = parent
        return "2015"

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
        semantic_recovery = self._semantic_recovery_guidance(segment)
        guidance_text = ""
        if all_guidance:
            guidance_text = "\nKeep in mind:\n" + "\n".join(all_guidance) + "\n"
        recovery_text = ""
        if semantic_recovery:
            recovery_text = "\nSemantic recovery mode:\n" + "\n".join(semantic_recovery) + "\n"

        return [
            mk_message(
                f"""\
Executing the test yields an error, shown below.
Modify or rewrite the test to correct it; respond only with the complete Rust test file in ```rust backticks.
Use the get_info tool function if you need to understand types or function signatures.

{error}
{recovery_text}
{guidance_text}"""
            )
        ]

    def missing_coverage_prompt(
        self, segment, missing_lines: set, missing_branches: set
    ) -> T.List[dict] | None:
        desc = lines_branches_do(missing_lines, set(), missing_branches)
        filename = segment.path.relative_to(self.args.src_base_dir)
        all_guidance = self._dynamic_rust_guidance(segment)
        semantic_recovery = self._semantic_recovery_guidance(segment)
        coverage_stall = self._coverage_stall_guidance(segment)
        guidance_text = ""
        if all_guidance:
            guidance_text = "\nRemember:\n" + "\n".join(all_guidance) + "\n"
        recovery_text = ""
        if semantic_recovery:
            recovery_text = "\nSemantic recovery mode:\n" + "\n".join(semantic_recovery) + "\n"
        if coverage_stall:
            recovery_text += "\nCoverage-stall mode:\n" + "\n".join(coverage_stall) + "\n"

        return [
            mk_message(
                f"""\
The tests still lack coverage: {desc} not execute.
Modify the tests to correct that; respond only with the complete Rust test file in ```rust backticks.
Use the get_info tool function if you need to understand more about the code.
{recovery_text}\
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
        edition_guidance = ""
        if self._crate_edition == "2015":
            edition_guidance = (
                f"\n- IMPORTANT: This crate uses Rust 2015 imports. Add `extern crate {cn};` "
                f"before any `use {cn}::...` statements in integration tests."
            )
        api_summary = self._crate_api_summary()
        return f"""\
Constraints:
- Write tests as standalone functions annotated with `#[test]`. Do NOT wrap them in a `mod tests {{ }}` block — the test file is compiled as a standalone integration test.
- Always add `use {cn}::*;` or explicit `use {cn}::SomeType;` imports at the top so that production types and functions are in scope. Do NOT use `use super::*;` — that only works for inline test modules.
- Always keep crate-root imports compatible with the crate edition.{edition_guidance}
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
                "any references; use owned types (String, Vec) where possible in tests. "
                "When borrowing a temporary (for example from `join()` or `to_string()`), "
                "bind it to a local `let` first."
            )

        # Functions that take an explicit Algorithm parameter
        if re.search(r'\balg\s*:\s*Algorithm\b', seg_text):
            hints.append(
                "- This API expects an explicit `Algorithm` argument. Pass a concrete variant "
                "such as `Algorithm::Myers`, `Algorithm::Patience`, or `Algorithm::Lcs` in the "
                "correct argument position."
            )

        # Generic index-based APIs are easy to misuse with &str / doubly-borrowed values
        if re.search(r'Index<\s*usize\s*>', seg_text):
            hints.append(
                "- This API relies on `Index<usize>`. Prefer concrete indexable containers such "
                "as slices, arrays, or `Vec<T>`. Do not add extra `&` borrows unless the signature "
                "explicitly expects them."
            )

        if (
            re.search(r'Range<\s*usize\s*>', seg_text)
            and ("slice" in seg_text.lower() or "remap" in seg_text.lower())
        ):
            hints.append(
                "- This code maps ranges/slices back into source values. Derive expected outputs "
                "from explicit start/end indices and contiguous spans; off-by-one mistakes are common."
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

    def _semantic_recovery_guidance(self, segment) -> list[str]:
        """Escalate to source-level semantic debugging after repeated failures."""
        if not getattr(self.args, "semantic_recovery", True):
            return []

        history = getattr(segment, "_retry_context", {}).get("history", [])
        current_ir = getattr(segment, "_current_ir", None)
        if len(history) < 2 or current_ir is None:
            return []

        recent = history[-3:]
        non_success = [h for h in recent if h.get("outcome") in {"F", "U", "timeout"}]
        if len(non_success) < 2:
            return []

        panic_like = {"panic", "assertion", "unknown"}
        current_cat = getattr(current_ir, "error_category", "")
        repeated_semantic = (
            current_cat in panic_like
            or sum(h.get("category") in panic_like for h in recent) >= 2
        )
        if not repeated_semantic:
            return []

        code_bits = [
            h.get("code")
            for h in recent
            if h.get("code")
        ]
        recent_codes = ", ".join(dict.fromkeys(code_bits))

        guidance = [
            f"- This segment has stalled for {len(non_success)} recent attempt(s) without a new `G`.",
        ]
        if recent_codes:
            guidance.append(
                f"- Recent compiler/runtime signals: {recent_codes}. Treat the current issue as a semantic misunderstanding, not just a syntax fix."
            )
        guidance.extend([
            "- Stop patching the previous test locally. Re-derive the target behavior from the implementation before writing assertions.",
            "- Use `get_info` on the target function, helper functions it calls, and any return/value types referenced in assertions.",
            "- Prefer one minimal test for one exact branch or behavior. Delete speculative extra assertions.",
            "- If earlier assertions failed, assume the expected value was guessed. Recompute it from the source logic, index arithmetic, or range transformations.",
            "- If exact full output is subtle, assert smaller invariants that are directly implied by the code path under test.",
        ])

        try:
            source = segment.path.read_text()
            lines = source.splitlines()
            seg_text = "\n".join(lines[max(0, segment.begin - 1): segment.end])
        except OSError:
            seg_text = ""

        if "slice" in seg_text.lower() or "remap" in seg_text.lower():
            guidance.append(
                "- For slice/remapper logic, derive the expected result from explicit slice boundaries and indices, not from tokenized English intuition."
            )
        if "iter_" in seg_text or "Iterator" in seg_text or "IntoIterator" in seg_text:
            guidance.append(
                "- For iterator-heavy code, check the yielded sequence element-by-element before asserting a fully aggregated output."
            )

        return guidance

    def _coverage_stall_guidance(self, segment) -> list[str]:
        """Tighten the objective after repeated useless coverage-only retries."""
        history = getattr(segment, "_retry_context", {}).get("history", [])
        if len(history) < 2:
            return []

        recent = history[-3:]
        recent_u = [h for h in recent if h.get("outcome") == "U"]
        if len(recent_u) < 2:
            return []

        guidance = [
            "- Do NOT add a broad suite on the next attempt. Write at most 1-2 tests total.",
            "- Pick blocker #1 and target only that blocker before trying to cover the rest of the segment.",
            "- Before writing assertions, make the branch shape obvious from the inputs. Prefer one small scenario whose DiffOp / match-arm / predicate path is easy to reason about.",
            "- Delete any test that does not directly contribute to blocker #1.",
        ]

        blockers = getattr(segment, "_latest_blockers", None) or []
        if blockers:
            blocker = blockers[0]
            target_lines = list(getattr(blocker, "target_lines", ()) or [])
            if target_lines:
                target_desc = (
                    str(target_lines[0])
                    if len(target_lines) == 1
                    else f"{target_lines[0]}-{target_lines[-1]}"
                )
                guidance.append(
                    f"- Primary blocker to hit first: lines {target_desc} are guarded by "
                    f"{blocker.predicate_kind.replace('_', ' ')} at line {blocker.predicate_line}: "
                    f"`{blocker.predicate_text}`"
                )
            if getattr(blocker, "hint", ""):
                guidance.append(
                    f"- Translate blocker #1 directly into input shape: {blocker.hint}"
                )
            variables = getattr(blocker, "variables", ()) or ()
            if variables:
                names = []
                for v in variables[:6]:
                    name = getattr(v, "name", "")
                    if name:
                        names.append(f"`{name}`")
                if names:
                    guidance.append(
                        f"- Drive these variables explicitly in the next test: {', '.join(names)}."
                    )

        return guidance

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
