import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import tempfile
import typing as T
from pathlib import Path

from ..segment import CodeSegment
from ..rust_codeinfo import (
    infer_branches,
    extract_impl_type,
    find_type_definition,
)
from .base import LanguageBackend
from ..diagnostic_ir import (
    DiagnosticIR, DiagnosticIRBuilder, ErrorCategory, Phase,
)


class RustBackend(LanguageBackend):
    """Backend implementation targeting Rust projects (cargo-based)."""

    language_id = "rust"

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.crate_root: Path = self._resolve_crate_root(args.package_dir)
        self._cargo_cmd = shutil.which("cargo") or "cargo"
        self._rustfmt_cmd = shutil.which("rustfmt")
        self._parser = None
        self._test_counter: dict[Path, int] = {}
        self._crate_name = self._detect_crate_name()
        self._crate_edition = self._detect_crate_edition()
        # llvm-cov availability
        self._has_llvm_cov = self._check_llvm_cov()
        # Detect nightly toolchain (needed for --branch flag)
        self._is_nightly = self._check_nightly()
        # Per-crate lock: serialise test-compile-run so concurrent tasks
        # don't clobber each other's temporary test files.
        self._crate_lock = asyncio.Lock()
        # Build crate public-API map (computed once, used by prompter)
        self._module_api_map = self._build_module_api_map()
        # Store on args so prompter can access it
        args._crate_name = self._crate_name
        args._crate_edition = self._crate_edition
        args._module_api_map = self._module_api_map
        # Build item→module lookup for auto-fixing imports
        self._item_module_lookup = self._build_item_module_lookup()

    def _check_llvm_cov(self) -> bool:
        """Check whether cargo-llvm-cov is installed."""
        try:
            result = subprocess.run(
                [self._cargo_cmd, "llvm-cov", "--version"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def _check_nightly(self) -> bool:
        """Check whether the active Rust toolchain is nightly."""
        try:
            result = subprocess.run(
                ["rustc", "--version"],
                capture_output=True, text=True, timeout=10,
            )
            return "nightly" in result.stdout.lower()
        except (OSError, subprocess.TimeoutExpired):
            return False

    def prepare_environment(self) -> None:
        if shutil.which(self._cargo_cmd) is None:
            raise RuntimeError(
                "Cargo executable not found. Ensure Rust is installed and 'cargo' is on PATH."
            )
        if not self._has_llvm_cov:
            raise RuntimeError(
                "cargo-llvm-cov not found. Install it with: cargo install cargo-llvm-cov\n"
                "Also ensure the llvm-tools component is installed: rustup component add llvm-tools-preview"
            )
        # Clean up leftover temp test files from previous runs
        for leftover in self.crate_root.rglob("coverup_tmp_*.rs"):
            try:
                leftover.unlink()
            except OSError:
                pass

    def initial_empty_coverage(self) -> dict:
        return {
            "meta": {"branch_coverage": False, "mode": "llvm-cov"},
            "files": {},
            "summary": {
                "covered_lines": 0,
                "missing_lines": 0,
                "covered_branches": 0,
                "missing_branches": 0,
                "percent_covered": 0.0,
            },
        }

    def measure_suite_coverage(
        self,
        *,
        pytest_args: str = "",
        isolate_tests: bool = False,
        branch_coverage: bool = True,
        trace=None,
        raise_on_failure: bool = True,
    ) -> dict:
        fd, temp_name = tempfile.mkstemp(prefix="coverup-rust-suite-", suffix=".json")
        os.close(fd)
        json_path = Path(temp_name)

        cmd = [
            self._cargo_cmd,
            "llvm-cov",
            "--json",
            "--output-path", str(json_path),
        ]

        # --branch requires nightly toolchain; skip on stable
        if branch_coverage and self._is_nightly:
            cmd.append("--branch")

        if trace:
            trace(cmd)

        try:
            run = subprocess.run(
                cmd,
                cwd=self.crate_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            if run.returncode != 0:
                if raise_on_failure:
                    raise subprocess.CalledProcessError(
                        run.returncode, cmd, output=run.stdout.encode()
                    )

            if json_path.exists() and json_path.stat().st_size > 0:
                coverage = parse_llvm_cov_json(
                    json_path, crate_root=self.crate_root
                )
            else:
                coverage = self.initial_empty_coverage()
        finally:
            json_path.unlink(missing_ok=True)

        return coverage

    async def measure_test_coverage(
        self,
        segment: CodeSegment,
        test_code: str,
        *,
        isolate_tests: bool,
        branch_coverage: bool,
        log_write: T.Callable[[str], None] | None,
    ) -> dict:
        # Determine path for temporary test
        src_dir = self._find_src_dir()
        task = asyncio.current_task()
        task_name = task.get_name() if task else "coverup"
        temp_name = f"coverup_tmp_{os.getpid()}_{task_name}_{segment.begin}.rs"
        temp_path = src_dir / temp_name

        # Prepare test code before acquiring lock
        prepared_code = self._prepare_test_code(test_code, segment)
        self._enforce_test_size(prepared_code, log_write)

        fd, json_tmp_name = tempfile.mkstemp(prefix="coverup-rust-test-", suffix=".json")
        os.close(fd)
        json_path = Path(json_tmp_name)

        # Serialize access to avoid concurrent compilation issues
        async with self._crate_lock:
            self._cleanup_temp_tests(src_dir)

            # Write the test module and register it
            temp_path.write_text(prepared_code)
            self._format_with_rustfmt(temp_path, log_write)

            # We need to ensure the module is included. We'll use a temporary
            # `#[cfg(test)]` approach: create a test file that cargo picks up.
            # In Rust, tests in the `tests/` dir are integration tests and
            # automatically compiled. For unit tests, they go in the source.
            # We'll add a mod declaration temporarily.
            mod_registration = self._register_temp_module(src_dir, temp_name, log_write)

            # Extract test function names for filtering
            test_names = self._extract_test_names(prepared_code)

            cmd = [
                self._cargo_cmd,
                "llvm-cov",
                "--json",
                "--output-path", str(json_path),
            ]
            # --branch requires nightly toolchain
            if branch_coverage and self._is_nightly:
                cmd.append("--branch")

            # Run tests single-threaded to avoid flaky results
            cmd.append("--")
            cmd.append("--test-threads=1")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.crate_root,
            )
            stdout, _ = await process.communicate()
            output = stdout.decode("utf-8", errors="ignore")
            if log_write:
                self._log_block(log_write, "[coverup] cargo llvm-cov stdout/stderr", output)

            if process.returncode != 0:
                # ── P3: Run cargo check --message-format=json for structured diagnostics ──
                # This is fast (~0.2s cached) and gives us error codes, spans,
                # and MachineApplicable suggested_replacement fields.
                self._last_check_diagnostics = []
                try:
                    check_proc = await asyncio.create_subprocess_exec(
                        self._cargo_cmd, "check", "--message-format=json",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=self.crate_root,
                    )
                    check_stdout, _ = await check_proc.communicate()
                    check_output = check_stdout.decode("utf-8", errors="ignore")
                    self._last_check_diagnostics = self.parse_cargo_check_json(check_output)
                    if log_write and self._last_check_diagnostics:
                        n_sug = sum(
                            len(d.get("suggestions", []))
                            for d in self._last_check_diagnostics
                        )
                        log_write(
                            f"[DIAG] cargo check found {len(self._last_check_diagnostics)} "
                            f"diagnostics, {n_sug} auto-fix suggestions"
                        )
                except Exception:
                    pass  # cargo check failed — fall through to normal error path

                # Clean up temp files before raising
                generated_code: str | None = None
                if temp_path.exists():
                    try:
                        generated_code = temp_path.read_text()
                    except OSError:
                        generated_code = "<unable to read generated test>"
                else:
                    generated_code = "<generated test file already removed>"

                if log_write and generated_code is not None:
                    self._log_block(
                        log_write,
                        "---- BEGIN generated test ----",
                        generated_code,
                        limit=16000,
                    )
                    log_write("\n---- END generated test ----\n")

                temp_path.unlink(missing_ok=True)
                self._unregister_temp_module(mod_registration, log_write)
                raise subprocess.CalledProcessError(
                    process.returncode, cmd, output=output.encode()
                )

            temp_path.unlink(missing_ok=True)
            self._unregister_temp_module(mod_registration, log_write)

        # Parse coverage
        if json_path.exists() and json_path.stat().st_size > 0:
            coverage = parse_llvm_cov_json(json_path, crate_root=self.crate_root)
        else:
            coverage = self.initial_empty_coverage()
        json_path.unlink(missing_ok=True)
        return coverage

    def extract_test_code(self, response_content: str) -> str | None:
        match = re.search(r"```rust\n(.*?)(?:```|\Z)", response_content, re.DOTALL)
        if not match:
            return None
        return match.group(1)

    def save_successful_test(
        self,
        segment: CodeSegment,
        test_code: str,
        asked: dict,
        gained: dict,
    ) -> T.Optional[str]:
        # Determine the best place to save the test
        src_dir = self._find_src_dir()
        counter = self._test_counter.setdefault(src_dir, 1)

        while True:
            filename = f"{self.args.prefix}_{counter:03d}_test.rs"
            path = src_dir / filename
            if not path.exists():
                break
            counter += 1

        self._test_counter[src_dir] = counter + 1

        header = (
            f"// file: {segment.identify()}\n"
            f"// asked: {json.dumps(asked if asked is not None else {})}\n"
            f"// gained: {json.dumps(gained if gained is not None else {})}\n\n"
        )
        prepared_code = self._prepare_test_code(test_code, segment)
        path.write_text(header + prepared_code)
        self._format_with_rustfmt(path, None)

        # Register the module permanently
        self._register_permanent_module(src_dir, filename)

        return path.as_posix()

    def get_missing_coverage(
        self,
        coverage: dict,
        *,
        line_limit: int,
    ) -> T.List[CodeSegment]:
        segments: list[CodeSegment] = []

        files = coverage.get("files", {})
        if not files:
            return self._segments_without_coverage(line_limit=line_limit)

        for filename, data in files.items():
            missing = set(data.get("missing_lines", []))
            if not missing:
                continue
            # Skip temp files
            if "coverup_tmp_" in Path(filename).name:
                continue
            # Skip test files
            if Path(filename).name.endswith("_test.rs"):
                continue
            executed = set(data.get("executed_lines", []))
            path = Path(filename).resolve()
            segments.extend(
                self._segments_for_file(
                    path,
                    missing_lines=missing,
                    executed_lines=executed,
                    line_limit=line_limit,
                )
            )

        return segments

    def _segments_without_coverage(self, *, line_limit: int) -> T.List[CodeSegment]:
        """Generate segments when no coverage data is available."""
        segments: list[CodeSegment] = []

        for path in sorted(self.crate_root.rglob("*.rs")):
            if "coverup_tmp_" in path.name:
                continue
            if path.name.endswith("_test.rs"):
                continue

            try:
                rel = path.relative_to(self.crate_root)
            except ValueError:
                continue

            if any(part.startswith(".") for part in rel.parts):
                continue
            if "target" in rel.parts:
                continue

            try:
                content = path.read_text()
            except OSError:
                continue

            line_count = len(content.splitlines())
            if line_count == 0:
                continue

            missing_lines = set(range(1, line_count + 1))
            segments.extend(
                self._segments_for_file(
                    path,
                    missing_lines=missing_lines,
                    executed_lines=set(),
                    line_limit=line_limit,
                )
            )

        return segments

    def format_test_error(self, output: str) -> str:
        """Extract key error information from verbose cargo test/build output."""
        lines = output.splitlines()
        error_lines: list[str] = []
        _markers = (
            'error[', 'error:', 'warning:', 'cannot find',
            'not found', 'mismatched types', 'expected ',
            'unused', 'dead_code', 'unreachable',
            'borrow', 'lifetime', 'move ', 'moved',
            'trait bound', 'no method named', 'no field',
            'private', 'unresolved', 'thread \'', 'panicked',
            'assertion', 'left:', 'right:', 'called `Result::unwrap()`',
            'called `Option::unwrap()`',
            'test result:', 'FAILED', 'failures:',
        )

        # Noise patterns to skip entirely
        _noise = (
            'exit status:',
            'error: process didn\'t exit successfully',
            'error: could not compile',
            'warning: build failed',
            'Compiling ',
            '-C instrument-coverage',
            '--crate-name ',
            'cargo fix --',
            '(run `cargo fix',
        )

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Skip noisy lines (long rustc commands, build metadata, etc.)
            if any(n in stripped for n in _noise):
                continue
            if any(m in stripped for m in _markers):
                error_lines.append(stripped)
                continue
            # Keep lines with file:line patterns in test files only
            if re.search(r'coverup.*\.rs:\d+', stripped):
                error_lines.append(stripped)
                continue
            # Keep "help:" suggestions from rustc
            if stripped.startswith("help:") or stripped.startswith("-->"):
                error_lines.append(stripped)
                continue

        # Filter out noise — only keep warnings if there are no real errors
        real_errors = [l for l in error_lines if not l.startswith('warning:')]
        if error_lines and not real_errors:
            return output[:3000] if len(output) > 3000 else output

        # Deduplicate identical error messages (common with repeated patterns)
        seen: set[str] = set()
        deduped: list[str] = []
        for line in error_lines:
            if line not in seen:
                seen.add(line)
                deduped.append(line)
        error_lines = deduped

        if error_lines:
            result = '\n'.join(error_lines[:50])
            if len(error_lines) > 50:
                result += f'\n... ({len(error_lines) - 50} more error lines omitted)'

            # Add import-related hints based on detected error patterns
            import_hints = self._generate_import_hints(result)
            if import_hints:
                result += '\n\nIMPORT FIX HINTS:\n' + '\n'.join(import_hints)

            structured_hints = self._generate_structured_fix_hints()
            if structured_hints:
                result += '\n\nSTRUCTURED FIX HINTS:\n' + '\n'.join(structured_hints)

            return result

        return output[:3000] if len(output) > 3000 else output

    def classify_error(self, output: str, phase: str = "compile") -> DiagnosticIR:
        """Classify a Rust compile/test error into DiagnosticIR."""
        formatted = self.format_test_error(output)
        cat, code = self._classify_rust_error(output)
        fixes: list[str] = []
        if cat == ErrorCategory.IMPORT.value:
            fixes.extend(self._generate_import_hints(formatted))
        fixes.extend(self._generate_structured_fix_hints())

        builder = (
            DiagnosticIRBuilder(language="rust", phase=phase)
            .fail()
            .tool("cargo")
            .error(cat, code, formatted)
            .suggested_fixes(list(dict.fromkeys(fixes)))
        )

        primary = self._first_primary_diagnostic()
        if primary:
            builder.location(
                file=primary.get("file_name", ""),
                start=primary.get("line_start", 0),
                end=primary.get("line_end", 0),
            )

        return builder.build()

    @staticmethod
    def _classify_rust_error(output: str) -> tuple:
        """Rust-specific error classification."""
        import re as _re
        m = _re.search(r'error\[(E\d+)\]', output)
        ecode = m.group(1) if m else ""
        text = output.lower()

        # Import-related errors
        if ecode in ("E0432", "E0433", "E0659", "E0425"):
            return ErrorCategory.IMPORT.value, ecode

        # Type-related errors
        if ecode in ("E0308", "E0277", "E0061", "E0107", "E0284", "E0599"):
            return ErrorCategory.TYPE.value, ecode

        # Visibility / access errors
        if ecode in ("E0603", "E0624"):
            return ErrorCategory.VISIBILITY.value, ecode

        # Ownership / borrow-checker errors
        if ecode in ("E0505", "E0382", "E0597", "E0716", "E0515", "E0502"):
            return ErrorCategory.OWNERSHIP.value, ecode

        # Syntax errors
        if ecode in ("E0063", "E0609"):
            return ErrorCategory.SYNTAX.value, ecode

        # Text-based fallbacks
        if "panicked" in text or "panic" in text:
            return ErrorCategory.PANIC.value, ecode
        if "assertion" in text:
            return ErrorCategory.ASSERTION.value, ecode
        if "private" in text or "inaccessible" in text:
            return ErrorCategory.VISIBILITY.value, ecode
        if "cannot find" in text or "not found" in text:
            return ErrorCategory.IMPORT.value, ecode
        if "mismatched types" in text or "expected" in text and "found" in text:
            return ErrorCategory.TYPE.value, ecode
        if ecode:
            return ErrorCategory.UNKNOWN.value, ecode
        if "error" in text:
            return ErrorCategory.UNKNOWN.value, ""
        return ErrorCategory.UNKNOWN.value, ""

    def _default_tool_name(self) -> str:
        return "cargo"

    # ── P3: Structured compiler diagnostics via cargo check ─────────

    def parse_cargo_check_json(self, raw_output: str) -> list[dict]:
        """Parse ``cargo check --message-format=json`` output.

        Returns a list of structured diagnostic dicts, each with:
          - code: str | None (e.g. "E0432")
          - level: str ("error" | "warning")
          - message: str
          - spans: list[dict]  (file_name, line_start, line_end, text, ...)
          - suggestions: list[dict] (replacement text, span, applicability)
          - children: list[dict] (sub-diagnostics, often "help: ...")
        """
        diagnostics: list[dict] = []
        for raw_line in raw_output.splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            if obj.get("reason") != "compiler-message":
                continue

            msg = obj.get("message", {})
            level = msg.get("level", "")
            if level not in ("error", "warning"):
                continue

            code_obj = msg.get("code")
            code_str = code_obj.get("code") if isinstance(code_obj, dict) else None

            spans = []
            for sp in msg.get("spans", []):
                spans.append({
                    "file_name": sp.get("file_name", ""),
                    "line_start": sp.get("line_start", 0),
                    "line_end": sp.get("line_end", 0),
                    "col_start": sp.get("column_start", 0),
                    "col_end": sp.get("column_end", 0),
                    "text": "\n".join(t.get("text", "") for t in sp.get("text", [])),
                    "label": sp.get("label", ""),
                    "is_primary": sp.get("is_primary", False),
                    "suggested_replacement": sp.get("suggested_replacement"),
                    "suggestion_applicability": sp.get("suggestion_applicability"),
                })

            suggestions: list[dict] = []
            for sp in spans:
                if sp["suggested_replacement"] is not None:
                    suggestions.append({
                        "replacement": sp["suggested_replacement"],
                        "file_name": sp["file_name"],
                        "line_start": sp["line_start"],
                        "line_end": sp["line_end"],
                        "col_start": sp["col_start"],
                        "col_end": sp["col_end"],
                        "applicability": sp.get("suggestion_applicability", ""),
                    })

            # Also look for suggestions in children
            children = []
            for child in msg.get("children", []):
                child_entry = {
                    "level": child.get("level", ""),
                    "message": child.get("message", ""),
                }
                for csp in child.get("spans", []):
                    repl = csp.get("suggested_replacement")
                    if repl is not None:
                        sug = {
                            "replacement": repl,
                            "file_name": csp.get("file_name", ""),
                            "line_start": csp.get("line_start", 0),
                            "line_end": csp.get("line_end", 0),
                            "col_start": csp.get("column_start", 0),
                            "col_end": csp.get("column_end", 0),
                            "applicability": csp.get("suggestion_applicability", ""),
                        }
                        suggestions.append(sug)
                children.append(child_entry)

            diagnostics.append({
                "code": code_str,
                "level": level,
                "message": msg.get("message", ""),
                "spans": spans,
                "suggestions": suggestions,
                "children": children,
            })

        return diagnostics

    def apply_machine_applicable_fixes(
        self, test_code: str, diagnostics: list[dict]
    ) -> tuple[str, list[str]]:
        """Apply MachineApplicable suggestions from cargo check to test code.

        Only applies fixes where ``suggestion_applicability`` is
        ``MachineApplicable`` (i.e. the compiler is certain the fix is correct).

        Returns ``(patched_code, list_of_fix_descriptions)``.
        """
        applied: list[str] = []
        lines = test_code.split('\n')

        # Collect all MachineApplicable suggestions, sorted by position
        # (apply in reverse order so line numbers stay valid)
        fixes: list[tuple[int, int, int, int, str, str]] = []
        for diag in diagnostics:
            for sug in diag.get("suggestions", []):
                if sug.get("applicability") != "MachineApplicable":
                    continue
                fixes.append((
                    sug["line_start"],
                    sug["col_start"],
                    sug["line_end"],
                    sug["col_end"],
                    sug["replacement"],
                    diag.get("code", "") or diag.get("message", "")[:40],
                ))

        if not fixes:
            return test_code, []

        # Sort by (line_start, col_start) descending so we apply bottom-up
        fixes.sort(key=lambda f: (f[0], f[1]), reverse=True)

        for line_start, col_start, line_end, col_end, replacement, desc in fixes:
            # Convert 1-based to 0-based indices
            ls = line_start - 1
            le = line_end - 1
            cs = col_start - 1
            ce = col_end - 1

            if ls < 0 or le >= len(lines):
                continue

            if ls == le:
                # Single-line replacement
                line = lines[ls]
                if cs >= 0 and ce <= len(line):
                    lines[ls] = line[:cs] + replacement + line[ce:]
                    applied.append(f"cargo_autofix({desc})")
            else:
                # Multi-line replacement
                first_line = lines[ls]
                last_line = lines[le]
                new_text = first_line[:cs] + replacement + last_line[ce:]
                lines[ls:le + 1] = [new_text]
                applied.append(f"cargo_autofix_multiline({desc})")

        return '\n'.join(lines), applied

    def _generate_import_hints(self, error_text: str) -> list[str]:
        """Generate specific import fix hints based on compiler errors."""
        hints: list[str] = []
        crate_name = (self._crate_name or 'crate').replace('-', '_')
        error_lower = error_text.lower()
        if self._crate_edition == "2015":
            crate_pat = re.escape(crate_name)
            if (
                re.search(rf'unresolved import [`\']?{crate_pat}[`\']?', error_text)
                or re.search(rf'unlinked crate [`\']?{crate_pat}[`\']?', error_text)
                or re.search(
                    rf'use of unresolved module or unlinked crate [`\']?{crate_pat}[`\']?',
                    error_text,
                )
                or (
                    "2015 edition" in error_lower
                    and crate_name in error_text
                    and "use " in error_text
                )
            ):
                hints.append(
                    f"- This crate uses Rust 2015 imports. Add `extern crate {crate_name};` "
                    f"before any `use {crate_name}::...` statements in the integration test."
                )

        lookup = self._item_module_lookup
        if not lookup:
            return hints

        unique = lookup.get("unique", {})

        # Detect "cannot find function/value X in this scope" or "undeclared type X"
        missing_items: set[str] = set()
        for m in re.finditer(
            r'cannot find (?:function|value|struct|type|trait) `(\w+)`', error_text
        ):
            missing_items.add(m.group(1))
        for m in re.finditer(r'undeclared type `(\w+)`', error_text):
            missing_items.add(m.group(1))

        # Check which of these items are in our known submodules
        suggested_imports: dict[str, list[str]] = {}
        for item in missing_items:
            if item in unique:
                mod = unique[item]
                if mod not in suggested_imports:
                    suggested_imports[mod] = []
                suggested_imports[mod].append(item)

        for mod, items in sorted(suggested_imports.items()):
            items_str = ', '.join(sorted(items)[:5])
            hints.append(
                f"- Items [{items_str}] are in `{crate_name}::{mod}`. "
                f"Add `use {crate_name}::{mod}::*;` to import them."
            )

        # Detect E0659 ambiguity
        if 'is ambiguous' in error_text:
            ambig_items = re.findall(r'`(\w+)` is ambiguous', error_text)
            for item in ambig_items:
                hints.append(
                    f"- `{item}` is ambiguous because it exists in multiple modules. "
                    f"Use an explicit import like `use {crate_name}::module::{item};` "
                    f"instead of wildcard imports."
                )

        return hints

    def _diagnostics_for_generated_test(self) -> list[dict]:
        """Return diagnostics most likely referring to the current generated test."""
        diagnostics = getattr(self, "_last_check_diagnostics", None) or []
        if not diagnostics:
            return []

        preferred: list[dict] = []
        for diag in diagnostics:
            spans = diag.get("spans", [])
            if any(
                "coverup_tmp_" in (sp.get("file_name") or "")
                or "/tests/" in (sp.get("file_name") or "").replace("\\", "/")
                or (sp.get("file_name") or "").replace("\\", "/").startswith("tests/")
                for sp in spans
            ):
                preferred.append(diag)

        return preferred or diagnostics

    def _first_primary_diagnostic(self) -> dict | None:
        """Return the first primary span from the latest compiler diagnostics."""
        for diag in self._diagnostics_for_generated_test():
            for sp in diag.get("spans", []):
                if sp.get("is_primary"):
                    return sp
        return None

    def _generate_structured_fix_hints(self, max_hints: int = 6) -> list[str]:
        """Translate structured cargo diagnostics into compact LLM-facing hints."""
        hints: list[str] = []
        seen: set[str] = set()

        for diag in self._diagnostics_for_generated_test():
            code = diag.get("code") or ""
            message = diag.get("message", "")
            primary_span = next(
                (sp for sp in diag.get("spans", []) if sp.get("is_primary")),
                None,
            )
            primary_label = (primary_span or {}).get("label") or ""

            def add_hint(text: str) -> None:
                text = text.strip()
                if not text:
                    return
                if not text.startswith("- "):
                    text = "- " + text
                if text not in seen:
                    seen.add(text)
                    hints.append(text)

            if code == "E0061":
                m = re.search(
                    r"argument #(\d+) of type `([^`]+)` is missing",
                    primary_label,
                )
                if m:
                    add_hint(
                        f"The call is missing argument #{m.group(1)} of type `{m.group(2)}`. "
                        "Match the function signature order exactly."
                    )
                if "help: provide the argument" in message.lower():
                    add_hint(
                        "Use the compiler's suggested call shape as the starting point instead of "
                        "guessing argument order."
                    )

            elif code == "E0603":
                mod_match = re.search(r"module `([^`]+)` is private", message)
                item_match = re.search(r"(?:struct|enum|type|function|constant) `([^`]+)` is private", message)
                if mod_match:
                    add_hint(
                        f"`{mod_match.group(1)}` is a private module. Import through a public "
                        "re-export or crate-root API instead of that module path."
                    )
                elif item_match:
                    add_hint(
                        f"`{item_match.group(1)}` is private. Do not import or reference it directly "
                        "from an integration test."
                    )

            elif code == "E0624":
                method_match = re.search(r"method `([^`]+)` is private", message)
                if method_match:
                    add_hint(
                        f"Method `{method_match.group(1)}` is private. Remove the direct call and "
                        "exercise it through a public API that reaches the same branch."
                    )

            elif code == "E0716":
                add_hint(
                    "A temporary is being borrowed too long. Bind the temporary to a local `let` "
                    "variable before taking references to it."
                )

            elif code == "E0277":
                if "cannot be indexed by `usize`" in message:
                    add_hint(
                        "Use an indexable container that matches the function's trait bounds "
                        "(e.g. slice/Vec/array), not a doubly-borrowed value."
                    )

            elif code == "E0308":
                if primary_label:
                    add_hint(
                        f"Match the exact type in the compiler label: {primary_label}"
                    )

            for child in diag.get("children", []):
                child_level = child.get("level", "")
                child_msg = (child.get("message") or "").strip()
                if not child_msg:
                    continue
                if child_level == "help":
                    if "consider using a `let` binding" in child_msg:
                        add_hint(
                            "Use a local `let` binding to give temporary values a longer lifetime "
                            "before borrowing them."
                        )
                    elif "consider removing the leading `&`-reference" in child_msg:
                        add_hint(
                            "If the compiler suggests removing a leading `&`, pass the value directly "
                            "instead of adding another borrow."
                        )
                    elif "provide the argument" in child_msg:
                        add_hint(
                            "Insert the missing argument(s) exactly where the compiler indicates."
                        )
                    else:
                        add_hint(f"Compiler help: {child_msg}")

            if len(hints) >= max_hints:
                break

        return hints[:max_hints]

    # ====================================================================
    #  Internal helpers
    # ====================================================================

    def _ensure_parser(self):
        if self._parser is not None:
            return
        try:
            from tree_sitter import Parser  # type: ignore[import-not-found]
            from tree_sitter_languages import get_language  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "Rust backend requires 'tree_sitter' and 'tree_sitter_languages' packages"
            ) from exc
        self._parser = Parser()
        self._parser.set_language(get_language("rust"))

    @staticmethod
    def _resolve_crate_root(package_dir: Path) -> Path:
        """Locate the crate root (directory containing Cargo.toml).

        If *package_dir* already contains Cargo.toml, return it as-is.
        Otherwise walk up the directory tree until we find Cargo.toml.
        This handles the common case where a user passes ``--source-dir
        <crate>/src`` instead of the crate root.
        """
        candidate = package_dir.resolve()
        # Walk up at most 5 levels to find Cargo.toml
        for _ in range(6):
            if (candidate / "Cargo.toml").exists():
                return candidate
            parent = candidate.parent
            if parent == candidate:
                break
            candidate = parent
        # Fall back to the original path
        return package_dir.resolve()

    def _find_src_dir(self) -> Path:
        """Find the main source directory for the crate."""
        src = self.crate_root / "src"
        if src.is_dir():
            return src
        return self.crate_root

    def _detect_crate_name(self) -> str | None:
        """Read the crate name from Cargo.toml."""
        cargo_toml = self.crate_root / "Cargo.toml"
        if not cargo_toml.exists():
            return None
        try:
            content = cargo_toml.read_text()
            match = re.search(r'name\s*=\s*"([^"]+)"', content)
            return match.group(1) if match else None
        except OSError:
            return None

    def _detect_crate_edition(self) -> str:
        """Read the crate edition from Cargo.toml.

        Cargo defaults crates without an explicit edition to Rust 2015, so we
        mirror that behavior here. This matters for integration tests because
        `use crate_name::...` requires `extern crate crate_name;` on Rust 2015.
        """
        cargo_toml = self.crate_root / "Cargo.toml"
        if not cargo_toml.exists():
            return "2015"
        try:
            content = cargo_toml.read_text()
        except OSError:
            return "2015"

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
        if not edition_match:
            return "2015"
        return edition_match.group(1)

    # ----------------------------------------------------------------
    #  Module public-API map
    # ----------------------------------------------------------------

    def _build_module_api_map(self) -> dict:
        """Scan the crate's ``lib.rs`` and public ``mod.rs`` files to build
        a map of module visibility and re-exports.

        Returns a dict with:
        - ``root_reexports``: list of ``pub use`` paths from lib.rs
          (e.g. ``["self::common::*", "self::text::*", "self::types::*"]``)
        - ``public_modules``: set of module names declared with ``pub mod``
          in lib.rs (e.g. ``{"algorithms", "iter", "udiff", "utils"}``)
        - ``private_modules``: set of module names declared with ``mod``
          (no pub) in lib.rs (e.g. ``{"common", "text", "types"}``)
        - ``submodule_reexports``: dict mapping public module name to list
          of re-exported item names
          (e.g. ``{"algorithms": ["Capture", "Compact", "DiffHook", ...]}``)
        - ``submodule_public_mods``: dict mapping public module name to set
          of its ``pub mod`` children
          (e.g. ``{"algorithms": {"lcs", "myers", "patience"}}``)
        """
        result: dict = {
            "root_reexports": [],
            "public_modules": set(),
            "private_modules": set(),
            "submodule_reexports": {},
            "submodule_public_mods": {},
            "module_pub_items": {},       # mod → {"functions": [...], "types": [...]}
        }

        lib_rs = self.crate_root / "src" / "lib.rs"
        if not lib_rs.exists():
            return result

        try:
            lib_text = lib_rs.read_text()
        except OSError:
            return result

        # Parse lib.rs for module declarations and re-exports
        for line in lib_text.splitlines():
            stripped = line.strip()
            # Skip lines inside doc comments, cfg attributes, etc.
            if stripped.startswith("//"):
                continue

            # pub mod X;
            m = re.match(r'^pub\s+mod\s+(\w+)\s*;', stripped)
            if m:
                result["public_modules"].add(m.group(1))
                continue

            # mod X;  (private)
            m = re.match(r'^mod\s+(\w+)\s*;', stripped)
            if m:
                result["private_modules"].add(m.group(1))
                continue

            # pub use self::modname::*;  or  pub use self::modname::Item;
            m = re.match(r'^pub\s+use\s+(self::)?(.+);', stripped)
            if m:
                result["root_reexports"].append(m.group(2).rstrip(';'))
                continue

        # For each public module, scan its mod.rs for re-exports and sub-modules
        src_dir = self.crate_root / "src"
        for mod_name in result["public_modules"]:
            mod_file = src_dir / mod_name / "mod.rs"
            if not mod_file.exists():
                mod_file = src_dir / f"{mod_name}.rs"
            if not mod_file.exists():
                continue

            try:
                mod_text = mod_file.read_text()
            except OSError:
                continue

            reexports: list[str] = []
            pub_submods: set[str] = set()
            pub_fns: list[str] = []
            pub_types: list[str] = []

            for mline in mod_text.splitlines():
                ms = mline.strip()
                if ms.startswith("//"):
                    continue

                # pub use item::Name;
                um = re.match(r'^pub\s+use\s+(?:self::)?(\w+)::(\w+(?:::\{[^}]+\})?)\s*;', ms)
                if um:
                    reexports.append(um.group(2))
                    continue
                # pub use item::{A, B};
                um2 = re.match(r'^pub\s+use\s+(?:self::)?(\w+)::\{([^}]+)\}\s*;', ms)
                if um2:
                    for item in um2.group(2).split(','):
                        reexports.append(item.strip())
                    continue
                # pub use crate::X;
                um3 = re.match(r'^pub\s+use\s+crate::(\w+)\s*;', ms)
                if um3:
                    reexports.append(um3.group(1))
                    continue

                # pub mod submod;
                sm = re.match(r'^pub\s+mod\s+(\w+)\s*;', ms)
                if sm:
                    pub_submods.add(sm.group(1))
                    continue

                # pub fn name(...)  — exclude pub(crate)
                # Use original line (not stripped) to only match top-level items
                fm = re.match(r'^pub\s+fn\s+(\w+)', mline)
                if fm:
                    pub_fns.append(fm.group(1))
                    continue
                # pub struct Name
                stm = re.match(r'^pub\s+struct\s+(\w+)', mline)
                if stm:
                    pub_types.append(stm.group(1))
                    continue
                # pub enum Name
                em = re.match(r'^pub\s+enum\s+(\w+)', mline)
                if em:
                    pub_types.append(em.group(1))
                    continue
                # pub trait Name
                trm = re.match(r'^pub\s+trait\s+(\w+)', mline)
                if trm:
                    pub_types.append(trm.group(1))
                    continue
                # pub type Name
                tym = re.match(r'^pub\s+type\s+(\w+)', mline)
                if tym:
                    pub_types.append(tym.group(1))
                    continue

            if reexports:
                result["submodule_reexports"][mod_name] = reexports
            if pub_submods:
                result["submodule_public_mods"][mod_name] = pub_submods
            if pub_fns or pub_types:
                result["module_pub_items"][mod_name] = {
                    "functions": pub_fns,
                    "types": pub_types,
                }

        return result

    def _build_item_module_lookup(self) -> dict:
        """Build a mapping of public item names to their module paths.

        Returns a dict with:
        - ``unique``: dict mapping item_name → module_name (only for items
          in exactly one public module, i.e. unambiguous)
        - ``ambiguous``: dict mapping item_name → [module_names] (items
          available from multiple public modules)
        """
        api_map = self._module_api_map
        if not api_map:
            return {"unique": {}, "ambiguous": {}}

        item_modules: dict[str, list[str]] = {}

        for mod_name in api_map.get("public_modules", set()):
            # Collect all public items from this module
            all_items: list[str] = []

            reexports = api_map.get("submodule_reexports", {}).get(mod_name, [])
            all_items.extend(reexports)

            pub_items = api_map.get("module_pub_items", {}).get(mod_name, {})
            all_items.extend(pub_items.get("functions", []))
            all_items.extend(pub_items.get("types", []))

            for item in all_items:
                if item not in item_modules:
                    item_modules[item] = []
                if mod_name not in item_modules[item]:
                    item_modules[item].append(mod_name)

        unique = {}
        ambiguous = {}
        for item, modules in item_modules.items():
            if len(modules) == 1:
                unique[item] = modules[0]
            else:
                ambiguous[item] = modules

        return {"unique": unique, "ambiguous": ambiguous}

    def _compute_import_hint(self, file_path: Path) -> str | None:
        """Given a source file path, produce a hint about the correct import path.

        Returns a string hint or None if no special guidance is needed.
        """
        api_map = self._module_api_map
        if not api_map or not api_map.get("public_modules"):
            return None

        crate_name = (self._crate_name or 'crate').replace('-', '_')
        src_dir = self.crate_root / "src"

        try:
            rel = file_path.relative_to(src_dir)
        except ValueError:
            return None

        parts = list(rel.parts)
        if not parts:
            return None

        # Determine the top-level module this file belongs to
        # e.g. "algorithms/compact.rs" → top_mod="algorithms", sub="compact"
        # e.g. "common.rs" → top_mod="common", sub=None
        # e.g. "algorithms/mod.rs" → top_mod="algorithms", sub=None
        if len(parts) == 1:
            # Direct file under src/
            fname = parts[0]
            if fname in ("lib.rs", "main.rs"):
                return None
            top_mod = fname.replace(".rs", "")
            sub_mod = None
        else:
            top_mod = parts[0]
            fname = parts[-1]
            if fname == "mod.rs":
                sub_mod = None
            else:
                sub_mod = fname.replace(".rs", "")

        hint_parts: list[str] = []

        # Case 1: File is in a PRIVATE module that's re-exported at root
        if top_mod in api_map.get("private_modules", set()):
            hint_parts.append(
                f"This file is in a PRIVATE module (`{top_mod}`). "
                f"Its public items are re-exported at the crate root. "
                f"Use `use {crate_name}::*;` or `use {crate_name}::ItemName;` to import them. "
                f"Do NOT use `use {crate_name}::{top_mod}::...;` — that path is private."
            )

        # Case 2: File is in a PUBLIC module
        elif top_mod in api_map.get("public_modules", set()):
            if sub_mod is None:
                # The mod.rs or top-level module file itself
                reexports = api_map.get("submodule_reexports", {}).get(top_mod, [])
                pub_submods = api_map.get("submodule_public_mods", {}).get(top_mod, set())
                pub_items = api_map.get("module_pub_items", {}).get(top_mod, {})
                if reexports:
                    items_str = ", ".join(reexports[:15])
                    hint_parts.append(
                        f"Public items from this module are available via "
                        f"`use {crate_name}::{top_mod}::{{...}};`. "
                        f"Available re-exported items: {items_str}."
                    )
                elif pub_items:
                    # Single-file public module with no re-exports — list pub items directly
                    fns = pub_items.get("functions", [])
                    types = pub_items.get("types", [])
                    hint_parts.append(
                        f"Items from this module must be imported via "
                        f"`use {crate_name}::{top_mod}::*;` or "
                        f"`use {crate_name}::{top_mod}::ItemName;`. "
                        f"Do NOT call these functions without the module path."
                    )
                    if fns:
                        fn_str = ", ".join(fns[:12])
                        hint_parts.append(f"Available functions: {fn_str}.")
                    if types:
                        type_str = ", ".join(types[:12])
                        hint_parts.append(f"Available types: {type_str}.")
                if pub_submods:
                    submods_str = ", ".join(sorted(pub_submods))
                    hint_parts.append(
                        f"Public sub-modules: {submods_str} "
                        f"(accessible via `use {crate_name}::{top_mod}::<submod>::...;`)."
                    )
            else:
                # File in a sub-module (e.g. algorithms/compact.rs)
                # Check if the sub-module itself is public or private
                pub_submods = api_map.get("submodule_public_mods", {}).get(top_mod, set())
                reexports = api_map.get("submodule_reexports", {}).get(top_mod, [])

                if sub_mod in pub_submods:
                    hint_parts.append(
                        f"This file is in the PUBLIC sub-module `{crate_name}::{top_mod}::{sub_mod}`. "
                        f"Use `use {crate_name}::{top_mod}::{sub_mod}::...;` to import items."
                    )
                else:
                    # Private sub-module — items re-exported by the parent
                    hint_parts.append(
                        f"This file is in a PRIVATE sub-module (`{sub_mod}`). "
                        f"Do NOT use `use {crate_name}::{top_mod}::{sub_mod}::...;` — that path is private and will cause E0432/E0603. "
                        f"Instead, use `use {crate_name}::{top_mod}::ItemName;` for items re-exported by the `{top_mod}` module."
                    )
                    if reexports:
                        items_str = ", ".join(reexports[:15])
                        hint_parts.append(
                            f"Items re-exported by `{crate_name}::{top_mod}`: {items_str}."
                        )

        return " ".join(hint_parts) if hint_parts else None

    def _segments_for_file(
        self,
        path: Path,
        *,
        missing_lines: set[int],
        executed_lines: set[int],
        line_limit: int,
    ) -> T.List[CodeSegment]:
        self._ensure_parser()
        source_bytes = path.read_bytes()
        tree = self._parser.parse(source_bytes)

        # ---- Exclude #[cfg(test)] mod blocks ----
        # These are the crate's own test modules; we should not try to
        # generate coverage for them.
        cfg_test_lines = self._collect_cfg_test_lines(tree.root_node)
        if cfg_test_lines:
            missing_lines = missing_lines - cfg_test_lines
            executed_lines = executed_lines - cfg_test_lines

        # Infer branch coverage
        exec_branches_list, miss_branches_list = infer_branches(
            path, executed_lines, missing_lines
        )
        all_missing_branches = set(
            (frm, to) for frm, to in miss_branches_list
        )

        branch_lines = set()
        for frm, to in all_missing_branches:
            branch_lines.add(frm)
            if to != 0:
                branch_lines.add(to)

        segments: list[CodeSegment] = []
        claimed_lines: set[int] = set()
        lines_of_interest = set(missing_lines) | branch_lines

        for line in sorted(lines_of_interest):
            if line in claimed_lines:
                continue

            node = self._find_enclosing_node(tree.root_node, line)
            if node is None:
                continue

            begin = node.start_point[0] + 1
            end = node.end_point[0] + 1
            if end <= begin:
                end = begin + 1

            # For large impl blocks, try to find a smaller enclosing element
            if node.type == "impl_item" and (end - begin) > line_limit:
                inner = self._find_enclosing_item_in_impl(node, line)
                if inner is not None:
                    begin = inner.start_point[0] + 1
                    end = inner.end_point[0] + 1

            claimed_lines.update(range(begin, end))

            name = self._node_name(node, source_bytes)
            line_range = set(range(begin, end))

            seg_missing_branches = {
                (frm, to) for frm, to in all_missing_branches
                if frm in line_range
            }

            # Build context: use declarations and impl type definition
            context = self._build_context(node, source_bytes, tree)
            imports = self._collect_use_statements(path)

            # Detect private items for prompt guidance
            priv_names = self._detect_private_items(node, source_bytes, tree.root_node)
            priv_methods = self._detect_private_methods(node, source_bytes)

            seg = CodeSegment(
                str(path),
                name,
                begin,
                end,
                lines_of_interest=lines_of_interest & line_range,
                missing_lines=missing_lines & line_range,
                executed_lines=executed_lines & line_range,
                missing_branches=seg_missing_branches,
                context=context,
                imports=imports,
            )
            # Attach private-item info as extra attribute for the prompter
            seg._private_items = priv_names  # type: ignore[attr-defined]
            seg._private_methods = priv_methods  # type: ignore[attr-defined]
            # Attach module import hint
            seg._import_hint = self._compute_import_hint(path)  # type: ignore[attr-defined]
            segments.append(seg)

        return segments

    # ----------------------------------------------------------------
    #  #[cfg(test)] detection
    # ----------------------------------------------------------------

    def _collect_cfg_test_lines(self, root_node) -> set[int]:
        """Return the set of 1-based line numbers inside ``#[cfg(test)] mod …`` blocks.

        These lines belong to the crate's own unit-test module and should
        be excluded from coverage analysis so we don't waste LLM calls
        trying to cover test helpers, test assertions, etc.
        """
        excluded: set[int] = set()
        children = list(root_node.children)
        for idx, child in enumerate(children):
            if child.type != "mod_item":
                continue
            # Check preceding sibling(s) for #[cfg(test)]
            is_cfg_test = False
            for back in range(idx - 1, max(idx - 5, -1), -1):
                prev = children[back]
                if prev.type == "attribute_item":
                    attr_text = prev.text
                    if isinstance(attr_text, bytes):
                        attr_text = attr_text.decode("utf-8", errors="ignore")
                    if "cfg(test)" in attr_text:
                        is_cfg_test = True
                        break
                elif prev.type not in ("line_comment", "block_comment"):
                    break
            if is_cfg_test:
                begin = child.start_point[0] + 1
                end = child.end_point[0] + 1
                excluded.update(range(begin, end + 1))
        return excluded

    # ----------------------------------------------------------------
    #  Private-item detection (for prompt guidance)
    # ----------------------------------------------------------------

    def _detect_private_items(
        self, node, source_bytes: bytes, root_node=None,
    ) -> list[str]:
        """Return names of private (non-pub) structs/fns/enums related to *node*.

        Used to generate a prompt hint telling the LLM not to import them
        directly.  When *node* is an ``impl_item``, also checks whether
        the **struct** being implemented is private (the most common
        cause of E0603 errors in integration tests).
        """
        private_names: list[str] = []
        targets = [node]
        # Also scan the impl body if node is impl_item
        if node.type == "impl_item":
            body = node.child_by_field_name("body")
            if body:
                targets = list(body.children)

            # ---- resolve the struct that this impl targets ----
            impl_type_name = self._impl_type_base_name(node, source_bytes)
            if impl_type_name and root_node is not None:
                for sibling in root_node.children:
                    if sibling.type == "struct_item":
                        sf = sibling.child_by_field_name("name")
                        if sf and source_bytes[sf.start_byte:sf.end_byte].decode(
                            "utf-8", errors="ignore"
                        ) == impl_type_name:
                            has_pub = any(
                                c.type == "visibility_modifier"
                                for c in sibling.children
                            )
                            if not has_pub and impl_type_name not in private_names:
                                private_names.append(impl_type_name)
                            break

        for n in targets:
            if n.type not in (
                "function_item", "struct_item", "enum_item",
                "type_item", "const_item", "static_item",
            ):
                continue
            has_pub = any(c.type == "visibility_modifier" for c in n.children)
            if has_pub:
                continue
            name_field = n.child_by_field_name("name")
            if name_field:
                name = source_bytes[name_field.start_byte:name_field.end_byte].decode(
                    "utf-8", errors="ignore"
                )
                if name not in private_names:
                    private_names.append(name)

        # Also check if the node itself is a private struct/fn
        if node.type in ("struct_item", "function_item", "enum_item"):
            has_pub = any(c.type == "visibility_modifier" for c in node.children)
            if not has_pub:
                name_field = node.child_by_field_name("name")
                if name_field:
                    name = source_bytes[name_field.start_byte:name_field.end_byte].decode(
                        "utf-8", errors="ignore"
                    )
                    if name not in private_names:
                        private_names.append(name)

        return private_names

    def _detect_private_methods(
        self, node, source_bytes: bytes,
    ) -> list[str]:
        """Return names of private (non-pub) methods inside an ``impl`` block.

        This is used to generate a specific E0624 warning in the prompt,
        telling the LLM it cannot call these methods from integration tests.
        """
        if node.type != "impl_item":
            return []
        body = node.child_by_field_name("body")
        if not body:
            return []
        private_methods: list[str] = []
        for child in body.children:
            if child.type != "function_item":
                continue
            has_pub = any(c.type == "visibility_modifier" for c in child.children)
            if has_pub:
                continue
            name_field = child.child_by_field_name("name")
            if name_field:
                name = source_bytes[name_field.start_byte:name_field.end_byte].decode(
                    "utf-8", errors="ignore"
                )
                if name not in private_methods:
                    private_methods.append(name)
        return private_methods

    @staticmethod
    def _impl_type_base_name(impl_node, source_bytes: bytes) -> str | None:
        """Extract the base type name from an ``impl Foo<T>`` node."""
        for child in impl_node.children:
            if child.type == "type_identifier":
                return source_bytes[child.start_byte:child.end_byte].decode(
                    "utf-8", errors="ignore"
                )
            if child.type == "generic_type":
                # e.g. GrowingHashmapChar<ValueType> → GrowingHashmapChar
                ident = child.child_by_field_name("type")
                if ident is None:
                    # fallback: first type_identifier child
                    for gc in child.children:
                        if gc.type == "type_identifier":
                            ident = gc
                            break
                if ident is not None:
                    return source_bytes[ident.start_byte:ident.end_byte].decode(
                        "utf-8", errors="ignore"
                    )
        return None

    def _find_enclosing_node(self, node, line: int):
        """Find the nearest enclosing declaration node for a given line."""
        for child in node.children:
            start = child.start_point[0] + 1
            end = child.end_point[0] + 1
            if start <= line <= end:
                if child.type in {
                    "function_item",
                    "impl_item",
                    "struct_item",
                    "enum_item",
                    "trait_item",
                    "const_item",
                    "static_item",
                    "type_item",
                    "mod_item",
                }:
                    return child
                result = self._find_enclosing_node(child, line)
                if result is not None:
                    return result
        return None

    def _find_enclosing_item_in_impl(self, impl_node, line: int):
        """Find a function_item inside an impl block that contains the given line."""
        body = impl_node.child_by_field_name("body")
        if not body:
            return None
        for child in body.children:
            if child.type == "function_item":
                start = child.start_point[0] + 1
                end = child.end_point[0] + 1
                if start <= line <= end:
                    return child
        return None

    def _node_name(self, node, source: bytes) -> str:
        """Extract the name of a declaration node."""
        name_field = node.child_by_field_name("name")
        if name_field is not None:
            return source[name_field.start_byte:name_field.end_byte].decode("utf-8")

        # For impl blocks, try to extract the type name
        if node.type == "impl_item":
            type_name = extract_impl_type(node, source)
            if type_name:
                return f"impl {type_name}"

        return "<anonymous>"

    def _build_context(
        self, node, source_bytes: bytes, tree
    ) -> list[tuple[int, int]]:
        """Build context lines for a segment (use statements, etc.)."""
        context: list[tuple[int, int]] = []

        # Include any use/extern crate at the top of the file
        for child in tree.root_node.children:
            if child.type in ("use_declaration", "extern_crate_declaration"):
                begin = child.start_point[0] + 1
                end = child.end_point[0] + 2
                context.append((begin, end))
            elif child.type not in ("line_comment", "block_comment", "attribute_item",
                                     "inner_attribute_item"):
                # Stop once we hit actual code (after use block)
                break

        # If the node is inside an impl, include the impl header
        if node.type == "function_item":
            parent = node.parent
            if parent and parent.type == "declaration_list":
                grandparent = parent.parent
                if grandparent and grandparent.type == "impl_item":
                    # Add the impl line itself
                    impl_line = grandparent.start_point[0] + 1
                    context.append((impl_line, impl_line + 1))

        return context

    def _collect_use_statements(self, path: Path) -> list[str]:
        """Collect use declarations from a Rust file."""
        imports: list[str] = []
        try:
            lines = path.read_text().splitlines(keepends=True)
        except OSError:
            return imports

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("use ") or stripped.startswith("extern crate "):
                imports.append(line)
            elif stripped.startswith("pub use "):
                imports.append(line)

        return imports

    def _prepare_test_code(self, test_code: str, segment: CodeSegment) -> str:
        """Ensure the test code has proper structure for Rust integration tests."""
        crate_name = (self._crate_name or 'crate').replace('-', '_')
        extern_stmt = f"extern crate {crate_name};"

        # Remove #[cfg(test)] / mod tests { } wrapper – not needed for integration tests
        code = test_code
        code = re.sub(r'#\[cfg\(test\)\]\s*', '', code)
        # Unwrap `mod tests { ... }` if the entire file is wrapped in it
        mod_match = re.match(
            r'^\s*mod\s+tests\s*\{(.*)\}\s*$',
            code, re.DOTALL,
        )
        if mod_match:
            code = mod_match.group(1).strip() + '\n'

        # Fix imports: replace `use super::*` with `use <crate>::*`
        code = re.sub(
            r'use\s+super::(\*|\{[^}]+\})',
            f'use {crate_name}::\\1',
            code,
        )

        # Fix `use crate::` → `use <crate>::` for integration tests
        # (In integration tests, `crate` refers to the test binary itself,
        #  not the library. The correct path is `use <crate_name>::...`.)
        code = re.sub(
            r'use\s+crate::',
            f'use {crate_name}::',
            code,
        )

        # Ensure there's at least one `use <crate>::` import
        has_crate_import = f'use {crate_name}::' in code
        if not has_crate_import:
            # Add `use <crate_name>::*;` at the top
            code = f'use {crate_name}::*;\n\n{code}'

        # Auto-fix submodule imports using the crate API map
        code = self._autofix_submodule_imports(code, crate_name)

        # Rust 2015 integration tests require `extern crate` for crate-root imports.
        if self._crate_edition == "2015" and not re.search(
            rf'^\s*extern\s+crate\s+{re.escape(crate_name)}\s*;',
            code,
            flags=re.MULTILINE,
        ):
            code = f'{extern_stmt}\n\n{code.lstrip()}'

        return code

    def _autofix_submodule_imports(self, code: str, crate_name: str) -> str:
        """Auto-add missing submodule imports and resolve import ambiguities.

        Uses the ``_item_module_lookup`` built from the crate API map to:
        1. Detect uses of items from public submodules that lack the
           correct ``use`` import.
        2. Add the missing ``use crate::submodule::*;`` imports.
        3. Resolve ambiguous glob imports (E0659) by converting
           conflicting globs to explicit imports.
        4. Fix wrong qualified paths like ``crate::item`` when the item
           is actually in ``crate::submodule::item``.
        """
        lookup = self._item_module_lookup
        if not lookup or not lookup.get("unique"):
            return code

        unique = lookup["unique"]      # item → single module
        ambiguous = lookup["ambiguous"]  # item → [modules]
        cn = re.escape(crate_name)

        # --- Step 1: Collect already-imported modules from use statements ---
        # Match `use crate_name::module::` or `use crate_name::module;`
        imported_modules: set[str] = set()
        for m in re.finditer(rf'use\s+{cn}::(\w+)(?:::|;)', code):
            imported_modules.add(m.group(1))

        # Detect glob imports: `use crate_name::module::*;`
        glob_modules: set[str] = set()
        for m in re.finditer(rf'use\s+{cn}::(\w+)::\*\s*;', code):
            glob_modules.add(m.group(1))

        # --- Step 2: Extract code body (skip use statements) for item detection ---
        code_lines = code.split('\n')
        body_lines = [l for l in code_lines
                      if not l.strip().startswith('use ')
                      and not l.strip().startswith('extern crate ')]
        code_body = '\n'.join(body_lines)

        # --- Step 3: Find items used in code body that need submodule imports ---
        needed_modules: set[str] = set()

        for item_name, mod_name in unique.items():
            if mod_name in imported_modules:
                continue
            # Check if item is used in the code body
            # Match function calls: item_name( or item_name::<
            # Match type uses: item_name< or item_name:: or standalone
            if re.search(rf'\b{re.escape(item_name)}\b', code_body):
                needed_modules.add(mod_name)

        # --- Step 4: Fix wrong qualified paths ---
        # LLM sometimes writes `crate_name::diff_slices(...)` when it should be
        # `crate_name::utils::diff_slices(...)`. Fix these qualified paths.
        for item_name, mod_name in unique.items():
            # Match `crate_name::item_name` but NOT `crate_name::module::item_name`
            wrong_path = rf'({cn})::({re.escape(item_name)})\b'
            # Ensure it's not already correctly qualified (no module:: before item)
            # Use negative lookbehind for `::` before the item
            pattern = rf'\b{cn}::(?!\w+::){re.escape(item_name)}\b'
            if re.search(pattern, code_body):
                # Replace `crate_name::item` with `crate_name::module::item`
                code = re.sub(
                    rf'\b({cn})::({re.escape(item_name)})\b',
                    rf'\1::{mod_name}::\2',
                    code,
                )

        # --- Step 5: Add missing submodule imports ---
        imports_to_add: list[str] = []
        for mod_name in sorted(needed_modules):
            import_stmt = f'use {crate_name}::{mod_name}::*;'
            # Don't add if it would create ambiguity with already-imported modules
            would_conflict = False
            for item_name, mods in ambiguous.items():
                if mod_name in mods:
                    # Check if another module with this item is already imported via glob
                    other_mods = [m for m in mods if m != mod_name and m in glob_modules]
                    if other_mods:
                        would_conflict = True
                        break
            if not would_conflict:
                imports_to_add.append(import_stmt)

        if imports_to_add:
            # Insert after existing use statements
            insert_text = '\n'.join(imports_to_add) + '\n'
            # Find the last use statement line
            last_use_idx = -1
            for i, line in enumerate(code_lines):
                if line.strip().startswith('use ') or line.strip().startswith('extern crate '):
                    last_use_idx = i
            if last_use_idx >= 0:
                code_lines.insert(last_use_idx + 1, insert_text.rstrip())
                code = '\n'.join(code_lines)
            else:
                code = insert_text + code

        # --- Step 6: Resolve ambiguous glob imports (E0659) ---
        # Re-scan for glob imports after additions
        glob_modules_final: list[str] = re.findall(
            rf'use\s+{cn}::(\w+)::\*\s*;', code
        )
        if len(glob_modules_final) > 1:
            glob_set = set(glob_modules_final)
            for item_name, mods in ambiguous.items():
                conflicting_globs = [m for m in mods if m in glob_set]
                if len(conflicting_globs) > 1:
                    # Check if the item is actually used in code
                    if re.search(rf'\b{re.escape(item_name)}\b', code_body):
                        # Keep the FIRST module's glob, remove the others,
                        # and add explicit imports for items from the removed module.
                        keep_mod = conflicting_globs[0]
                        for remove_mod in conflicting_globs[1:]:
                            code = re.sub(
                                rf'use\s+{cn}::{re.escape(remove_mod)}::\*\s*;\n?',
                                '',
                                code,
                                count=1,
                            )
                            glob_set.discard(remove_mod)
                            # Add back explicit imports for other items from the removed module
                            # that are actually used in the code
                            for other_item, other_mod in unique.items():
                                if other_mod == remove_mod and re.search(
                                    rf'\b{re.escape(other_item)}\b', code_body
                                ):
                                    explicit_import = f'use {crate_name}::{remove_mod}::{other_item};\n'
                                    code = explicit_import + code

        return code

    def _format_with_rustfmt(
        self, path: Path, log_write: T.Callable[[str], None] | None
    ) -> bool:
        """Format a Rust file with rustfmt."""
        if not self._rustfmt_cmd:
            return True

        try:
            result = subprocess.run(
                [self._rustfmt_cmd, str(path)],
                cwd=self.crate_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        except OSError as exc:
            if log_write:
                log_write(f"[coverup] failed to invoke rustfmt: {exc}\n")
            return False

        if result.returncode != 0 and log_write:
            self._log_block(
                log_write,
                f"[coverup] rustfmt exited with {result.returncode}:",
                result.stdout,
            )

        return result.returncode == 0

    def _cleanup_temp_tests(self, src_dir: Path) -> None:
        """Remove any leftover temporary test files."""
        for tmp in src_dir.glob("coverup_tmp_*.rs"):
            try:
                tmp.unlink()
            except OSError:
                continue

    def _register_temp_module(
        self, src_dir: Path, temp_filename: str,
        log_write: T.Callable[[str], None] | None
    ) -> dict | None:
        """Register a temporary test module in lib.rs or main.rs.

        Returns registration info dict for later cleanup, or None if
        using the integration test approach (tests/ directory).
        """
        # Strategy: place the test file in tests/ as an integration test
        # This avoids modifying lib.rs/main.rs
        tests_dir = self.crate_root / "tests"
        if tests_dir.is_dir() or not (src_dir / "lib.rs").exists():
            # Use integration test approach
            tests_dir.mkdir(exist_ok=True)
            src_path = src_dir / temp_filename
            dst_path = tests_dir / temp_filename
            if src_path.exists():
                # Move the file to tests/
                dst_path.write_text(src_path.read_text())
                src_path.unlink()
                return {"type": "integration", "path": str(dst_path)}

        # For library crates, we can add a #[cfg(test)] mod in lib.rs
        # but this is invasive. Prefer the integration test approach.
        tests_dir.mkdir(exist_ok=True)
        src_path = src_dir / temp_filename
        dst_path = tests_dir / temp_filename
        if src_path.exists():
            dst_path.write_text(src_path.read_text())
            src_path.unlink()
            return {"type": "integration", "path": str(dst_path)}

        return None

    def _unregister_temp_module(
        self, registration: dict | None,
        log_write: T.Callable[[str], None] | None
    ) -> None:
        """Remove a temporary test module registration."""
        if registration is None:
            return
        if registration["type"] == "integration":
            path = Path(registration["path"])
            path.unlink(missing_ok=True)

    def _register_permanent_module(self, src_dir: Path, filename: str) -> None:
        """Register a permanent test file.

        For Rust, integration tests in tests/ are automatically picked up,
        so we just need to ensure the file is in the right place.
        """
        tests_dir = self.crate_root / "tests"
        tests_dir.mkdir(exist_ok=True)

        src_path = src_dir / filename
        if src_path.exists() and src_dir != tests_dir:
            dst_path = tests_dir / filename
            dst_path.write_text(src_path.read_text())
            src_path.unlink()

    def _extract_test_names(self, code: str) -> list[str]:
        """Extract test function names from Rust test code."""
        names = []
        test_fn_pat = re.compile(r'#\[test\]\s*(?:#\[.*?\]\s*)*fn\s+(\w+)', re.DOTALL)
        for match in test_fn_pat.finditer(code):
            names.append(match.group(1))
        return names

    def _enforce_test_size(
        self,
        code: str,
        log_write: T.Callable[[str], None] | None,
        *,
        max_lines: int = 400,
        max_chars: int = 20000,
    ) -> None:
        line_count = code.count("\n") + 1
        char_count = len(code)
        if line_count <= max_lines and char_count <= max_chars:
            return

        msg = (
            f"[coverup] generated test has {line_count} lines / {char_count} chars, "
            f"which exceeds the limit ({max_lines} lines / {max_chars} chars)."
            " Trim the test scope or split cases before retrying."
        )
        if log_write:
            log_write(msg + "\n")
        raise RuntimeError(msg)

    def _log_block(
        self,
        log_write: T.Callable[[str], None] | None,
        header: str,
        text: str,
        *,
        limit: int = 8000,
    ) -> None:
        if log_write is None or not text:
            return

        clean_header = header.rstrip()
        if len(text) <= limit:
            log_write(f"{clean_header}\n{text}\n")
            return

        head = limit // 2
        tail = limit - head
        truncated_msg = (
            f"{clean_header} (truncated to {limit} chars)\n"
            f"{text[:head]}\n... (omitted) ...\n{text[-tail:]}\n"
        )
        log_write(truncated_msg)


# ====================================================================
#  Coverage profile parser for cargo-llvm-cov JSON output
# ====================================================================

def parse_llvm_cov_json(
    json_path: Path,
    *,
    crate_root: Path | None = None,
) -> dict:
    """Parse the JSON output from ``cargo llvm-cov --json``.

    The JSON follows the llvm-cov export format::

        {
          "data": [{
            "files": [{
              "filename": "src/lib.rs",
              "segments": [[line, col, count, hasCount, isRegionEntry, isGap], ...],
              "summary": { "lines": { "count": N, "covered": M, "percent": P } }
            }],
            "totals": { "lines": { ... }, "branches": { ... } }
          }]
        }
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {
            "meta": {"branch_coverage": False},
            "files": {},
            "summary": {
                "covered_lines": 0, "missing_lines": 0,
                "covered_branches": 0, "missing_branches": 0,
                "percent_covered": 0.0,
            },
        }

    files: dict[str, dict] = {}
    total_executed = 0
    total_missing = 0
    total_exec_branches = 0
    total_miss_branches = 0

    data_entries = raw.get("data", [])
    if not data_entries:
        return {
            "meta": {"branch_coverage": False},
            "files": {},
            "summary": {
                "covered_lines": 0, "missing_lines": 0,
                "covered_branches": 0, "missing_branches": 0,
                "percent_covered": 0.0,
            },
        }

    for data_entry in data_entries:
        for file_info in data_entry.get("files", []):
            filename = file_info.get("filename", "")
            if not filename:
                continue

            filepath = Path(filename)
            # Resolve relative to crate root
            if not filepath.is_absolute() and crate_root:
                filepath = (crate_root / filepath).resolve()

            if not filepath.exists():
                continue

            # Skip test files and temp files
            if filepath.name.endswith("_test.rs") or "coverup_tmp_" in filepath.name:
                continue

            file_key = str(filepath)

            # Parse segments to determine line coverage
            # Segments format: [line, col, count, hasCount, isRegionEntry, isGap?]
            segments = file_info.get("segments", [])
            executed_lines: set[int] = set()
            missing_lines: set[int] = set()

            # The segments describe regions. Between consecutive segment entries,
            # the count is the one from the previous segment entry.
            # A simpler approach: use the summary line data if available
            summary = file_info.get("summary", {})
            lines_summary = summary.get("lines", {})

            # Process segments to build line-level coverage
            if segments:
                _parse_segments_to_lines(segments, filepath, executed_lines, missing_lines)
            else:
                # If no segments, use summary data
                total_lines = lines_summary.get("count", 0)
                covered = lines_summary.get("covered", 0)
                total_executed += covered
                total_missing += total_lines - covered
                continue

            # Infer branch coverage
            exec_br_list, miss_br_list = [], []
            try:
                exec_br_list, miss_br_list = infer_branches(
                    filepath, executed_lines, missing_lines
                )
            except Exception:
                pass

            executed = sorted(executed_lines)
            missing = sorted(missing_lines)
            total = len(executed) + len(missing)
            covered_count = len(executed)

            files[file_key] = {
                "executed_lines": executed,
                "missing_lines": missing,
                "executed_branches": exec_br_list,
                "missing_branches": miss_br_list,
                "summary": {
                    "covered_lines": covered_count,
                    "missing_lines": len(missing),
                    "covered_branches": len(exec_br_list),
                    "missing_branches": len(miss_br_list),
                    "percent_covered": (covered_count / total * 100.0) if total else 100.0,
                },
            }

            total_executed += covered_count
            total_missing += len(missing)
            total_exec_branches += len(exec_br_list)
            total_miss_branches += len(miss_br_list)

    summary_total = total_executed + total_missing
    summary = {
        "covered_lines": total_executed,
        "missing_lines": total_missing,
        "covered_branches": total_exec_branches,
        "missing_branches": total_miss_branches,
        "percent_covered": (total_executed / summary_total * 100.0) if summary_total else 100.0,
    }

    return {
        "meta": {"branch_coverage": True, "mode": "llvm-cov"},
        "files": files,
        "summary": summary,
    }


def _parse_segments_to_lines(
    segments: list,
    filepath: Path,
    executed_lines: set[int],
    missing_lines: set[int],
) -> None:
    """Convert llvm-cov segments into line-level executed/missing sets.

    Each segment is: [line, col, count, hasCount, isRegionEntry, ...]
    Between two consecutive segments, the execution count is that of the
    first segment.  We accumulate the max count seen for each line.
    """
    # First pass: determine the range of lines in the file
    try:
        line_count = len(filepath.read_text().splitlines())
    except OSError:
        return

    # Build line -> max count mapping
    line_counts: dict[int, int] = {}

    for i, seg in enumerate(segments):
        if len(seg) < 4:
            continue
        seg_line = seg[0]
        seg_count = seg[2]
        has_count = seg[3]

        if not has_count:
            continue

        # Determine end line (next segment's line, or EOF)
        if i + 1 < len(segments):
            end_line = segments[i + 1][0]
        else:
            end_line = seg_line + 1

        for ln in range(seg_line, min(end_line + 1, line_count + 1)):
            if ln in line_counts:
                line_counts[ln] = max(line_counts[ln], seg_count)
            else:
                line_counts[ln] = seg_count

    for ln, count in line_counts.items():
        if count > 0:
            executed_lines.add(ln)
        else:
            missing_lines.add(ln)
