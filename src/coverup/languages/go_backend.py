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
from ..go_codeinfo import (
    infer_branches,
    extract_receiver_type,
    find_type_definition,
)
from .base import LanguageBackend
from ..diagnostic_ir import (
    DiagnosticIR, DiagnosticIRBuilder, ErrorCategory, Phase,
)


class GoBackend(LanguageBackend):
    """Backend implementation targeting Go projects."""

    language_id = "go"

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.module_root: Path = args.package_dir
        self._go_cmd = shutil.which("go") or "go"
        self._gofmt_cmd = shutil.which("gofmt")
        self._goimports_cmd = self._find_goimports()
        self._parser = None
        self._test_counter: dict[Path, int] = {}
        self._module_path = self._detect_module_path()
        self._package_cache: dict[Path, str] = {}
        # Per-package lock: serialise test-compile-run within the same Go
        # package directory so concurrent tasks don't clobber each other's
        # temporary test files or cause duplicate-symbol compilation errors.
        self._package_locks: dict[str, asyncio.Lock] = {}

    @staticmethod
    def _find_goimports() -> str | None:
        """Search for goimports in PATH, GOPATH/bin, and GOBIN."""
        found = shutil.which("goimports")
        if found:
            return found
        # Check GOBIN
        gobin = os.environ.get("GOBIN")
        if gobin:
            candidate = Path(gobin) / "goimports"
            if candidate.exists():
                return str(candidate)
        # Check GOPATH/bin (default ~/go/bin)
        gopath = os.environ.get("GOPATH", str(Path.home() / "go"))
        for gp in gopath.split(os.pathsep):
            candidate = Path(gp) / "bin" / "goimports"
            if candidate.exists():
                return str(candidate)
        # Also check ~/Tools/gopath/bin (common non-standard location)
        for extra in [Path.home() / "Tools" / "gopath" / "bin"]:
            candidate = extra / "goimports"
            if candidate.exists():
                return str(candidate)
        return None

    def _get_package_lock(self, package_dir: Path) -> asyncio.Lock:
        """Return (or create) the asyncio.Lock for the given package directory."""
        key = str(package_dir)
        if key not in self._package_locks:
            self._package_locks[key] = asyncio.Lock()
        return self._package_locks[key]

    def prepare_environment(self) -> None:
        if shutil.which(self._go_cmd) is None:
            raise RuntimeError(
                "Go executable not found. Ensure Go is installed and 'go' is on PATH."
            )
        # Clean up leftover temp test files from previous (possibly crashed) runs.
        # These would otherwise be compiled by 'go test' and could appear in
        # coverage data, creating bogus segments.
        for leftover in self.module_root.rglob("coverup_tmp_*.go"):
            try:
                leftover.unlink()
            except OSError:
                pass

    def initial_empty_coverage(self) -> dict:
        return {
            "meta": {"branch_coverage": False, "mode": "count"},
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
        fd, temp_name = tempfile.mkstemp(prefix="coverup-go-suite-", suffix=".out")
        os.close(fd)
        profile_path = Path(temp_name)
        cmd = [
            self._go_cmd,
            "test",
            "./...",
            "-covermode=count",
            f"-coverprofile={profile_path}",
            "-count=1",
        ]

        extra_args = getattr(self.args, "go_test_args", "")
        if extra_args:
            cmd.extend(extra_args.split())

        if trace:
            trace(cmd)

        try:
            run = subprocess.run(
                cmd,
                cwd=self.module_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            if run.returncode != 0:
                if raise_on_failure:
                    raise subprocess.CalledProcessError(
                        run.returncode, cmd, output=run.stdout.encode()
                    )
                # If we are continuing on failure, we still try to parse the coverage profile
                # below, as go test often produces it even if some tests fail.

            if profile_path.exists() and profile_path.stat().st_size > 0:
                coverage = parse_go_cover_profile(
                    profile_path,
                    module_root=self.module_root,
                    module_path=self._module_path,
                )
            else:
                coverage = {
                    "files": {},
                    "meta": {"branch_coverage": False},
                    "summary": {
                        "covered_lines": 0,
                        "missing_lines": 0,
                        "covered_branches": 0,
                        "missing_branches": 0,
                        "percent_covered": 0.0,
                    },
                }
        finally:
            profile_path.unlink(missing_ok=True)

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
        package_dir = segment.path.parent
        task = asyncio.current_task()
        task_name = task.get_name() if task else "coverup"
        temp_name = f"coverup_tmp_{os.getpid()}_{task_name}_{segment.begin}_test.go"
        temp_path = package_dir / temp_name

        # Prepare the test code BEFORE acquiring the lock (CPU-only work
        # that doesn't touch the filesystem in the package directory).
        header = self._make_header(segment, asked=None, gained=None, include_comments=False)
        prepared_code = self._prepare_test_code(test_code, segment)
        self._enforce_test_size(prepared_code, log_write)

        fd, temp_name = tempfile.mkstemp(prefix="coverup-go-test-", suffix=".out")
        os.close(fd)
        profile_path = Path(temp_name)

        # ---- CRITICAL SECTION: only one task per Go package at a time ----
        # Without this lock, concurrent tasks in the same package directory
        # clobber each other's temp test files and cause 100% USELESS results.
        pkg_lock = self._get_package_lock(package_dir)
        async with pkg_lock:
            self._cleanup_temp_tests(package_dir)
            # _ensure_unique_test_names must run inside the lock so it sees the
            # true set of existing names (no other temp file present).
            prepared_code = self._ensure_unique_test_names(package_dir, prepared_code)
            temp_path.write_text(header + prepared_code)
            formatted_ok = self._format_with_goimports(temp_path, log_write)

            package_pattern = self._package_pattern(package_dir)
            cmd = [
                self._go_cmd,
                "test",
                package_pattern,
                "-covermode=count",
                f"-coverprofile={profile_path}",
                "-count=1",
            ]

            extra_args = getattr(self.args, "go_test_args", "")
            if extra_args:
                cmd.extend(extra_args.split())

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.module_root,
            )
            stdout, _ = await process.communicate()
            output = stdout.decode("utf-8", errors="ignore")
            if log_write:
                self._log_block(
                    log_write,
                    "[coverup] go test stdout/stderr",
                    output,
                )

            if process.returncode != 0:
                # Attempt to fix missing dependencies and retry
                if "no required module provides package" in output or "cannot find package" in output:
                    if log_write:
                        log_write("[coverup] detected missing dependencies, attempting 'go mod tidy'...\n")
                    self._run_go_mod_tidy(log_write)
                    # Retry the test after tidy
                    process2 = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT,
                        cwd=self.module_root,
                    )
                    stdout2, _ = await process2.communicate()
                    output2 = stdout2.decode("utf-8", errors="ignore")
                    if log_write:
                        self._log_block(log_write, "[coverup] retry after tidy", output2)
                    if process2.returncode == 0:
                        # Retry succeeded – parse coverage and return
                        temp_path.unlink(missing_ok=True)
                        if profile_path.exists() and profile_path.stat().st_size > 0:
                            coverage = parse_go_cover_profile(
                                profile_path,
                                module_root=self.module_root,
                                module_path=self._module_path,
                            )
                        else:
                            coverage = self.initial_empty_coverage()
                        profile_path.unlink(missing_ok=True)
                        return coverage
                    # Retry also failed – fall through to error handling
                    output = output2

                profile_path.unlink(missing_ok=True)
                generated_code: str | None = None
                if temp_path.exists():
                    try:
                        generated_code = temp_path.read_text()
                    except OSError as exc:  # pragma: no cover - diagnostic path
                        generated_code = f"<unable to read generated test: {exc}>"
                else:
                    generated_code = "<generated test file already removed>"

                if log_write and not formatted_ok:
                    log_write(
                        "[coverup] formatter reported errors before go test failure; "
                        "generated test may contain syntax issues.\n"
                    )

                if log_write and generated_code is not None:
                    self._log_block(
                        log_write,
                        "---- BEGIN generated test ----",
                        generated_code,
                        limit=16000,
                    )
                    log_write("\n---- END generated test ----\n")

                temp_path.unlink(missing_ok=True)
                # Pass the FULL go test output so format_test_error can extract
                # real compile errors (not just a one-line summary).
                raise subprocess.CalledProcessError(
                    process.returncode, cmd, output=output.encode()
                )

            temp_path.unlink(missing_ok=True)
        # ---- END CRITICAL SECTION ----

        coverage = parse_go_cover_profile(
            profile_path,
            module_root=self.module_root,
            module_path=self._module_path,
        )
        profile_path.unlink(missing_ok=True)
        return coverage

    def extract_test_code(self, response_content: str) -> str | None:
        match = re.search(r"```go\n(.*?)(?:```|\Z)", response_content, re.DOTALL)
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
        package_dir = segment.path.parent
        counter = self._test_counter.setdefault(package_dir, 1)

        while True:
            filename = f"{self.args.prefix}_{counter:03d}_test.go"
            path = package_dir / filename
            disabled = package_dir / f"disabled_{filename}"
            if not path.exists() and not disabled.exists():
                break
            counter += 1

        self._test_counter[package_dir] = counter + 1

        header = self._make_header(segment, asked=asked, gained=gained)
        prepared_code = self._prepare_test_code(test_code, segment)
        prepared_code = self._ensure_unique_test_names(package_dir, prepared_code)
        path.write_text(header + prepared_code)
        self._format_with_goimports(path, None)

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
            # Skip leftover temp files that may have leaked into coverage data
            if "coverup_tmp_" in Path(filename).name:
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
        segments: list[CodeSegment] = []

        for path in sorted(self.module_root.rglob("*.go")):
            if path.name.endswith("_test.go"):
                continue
            if "coverup_tmp_" in path.name:
                continue

            try:
                rel = path.relative_to(self.module_root)
            except ValueError:
                continue

            if any(part.startswith(".") for part in rel.parts):
                continue
            if "vendor" in rel.parts:
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
        """Extract key error information from verbose go test output.

        Filters the raw `go test` stdout/stderr to keep only lines that
        contain real compile errors, test failures, panics, or assertion
        messages.  Lines from *existing* tests that merely report
        "could not compile test program" are skipped so that the actual
        compiler diagnostics are surfaced to the LLM.
        """
        lines = output.splitlines()
        error_lines: list[str] = []
        # Markers that indicate a useful error/diagnostic line
        _markers = (
            'undefined:', 'cannot ', 'imported and not used',
            'syntax error', 'too many', 'not enough',
            'does not implement', 'cannot use', 'redeclared',
            'duplicate ', 'not a type', 'invalid ', 'missing ',
            'panic:', '--- FAIL', 'FAIL\t',
            'Error(', 'Fatal(',
            'got ', 'want ', 'expected ',
            'unknown ', 'unresolved ', 'declared and not used',
            'no such file or directory', 'type mismatch',
            'has no field or method', 'not exported',
            'unexported ',
        )
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Skip the unhelpful wrapper line from existing tests
            # e.g. "cobra_test.go:291: could not compile test program: ..."
            if 'could not compile test program' in stripped:
                continue
            # Keep genuine compile errors (contain .go: with a line number)
            if '.go:' in stripped and any(m in stripped for m in _markers):
                error_lines.append(stripped)
                continue
            # Keep any line with a .go:<digits> pattern (likely a compile error)
            if re.search(r'\.go:\d+', stripped):
                error_lines.append(stripped)
                continue
            # Keep other marker lines (but not bare FAIL lines if we have
            # better diagnostics already)
            if any(m in stripped for m in _markers):
                error_lines.append(stripped)
        # If the only captured lines are bare "FAIL ..." summaries, fall
        # back to the full output so the LLM sees actual diagnostics.
        real_errors = [l for l in error_lines if not l.startswith('FAIL')]
        if error_lines and not real_errors:
            # Only FAIL summaries were captured; return full output instead
            return output[:3000] if len(output) > 3000 else output
        # Limit to avoid wasting tokens
        if error_lines:
            result = '\n'.join(error_lines[:40])
            if len(error_lines) > 40:
                result += f'\n... ({len(error_lines) - 40} more error lines omitted)'
            return result
        # Fallback: return truncated original
        return output[:3000] if len(output) > 3000 else output

    def classify_error(self, output: str, phase: str = "compile") -> DiagnosticIR:
        """Classify a Go compile/test error into DiagnosticIR."""
        formatted = self.format_test_error(output)
        cat, code = self._classify_go_error(output)
        return (
            DiagnosticIRBuilder(language="go", phase=phase)
            .fail()
            .tool("go test")
            .error(cat, code, formatted)
            .build()
        )

    @staticmethod
    def _classify_go_error(output: str) -> tuple:
        text = output.lower()
        if "imported and not used" in text or "undefined:" in text:
            return ErrorCategory.IMPORT.value, ""
        if "cannot use" in text or "type mismatch" in text:
            return ErrorCategory.TYPE.value, ""
        if "unexported" in text or "not exported" in text:
            return ErrorCategory.VISIBILITY.value, ""
        if "does not implement" in text:
            return ErrorCategory.INTERFACE.value, ""
        if "syntax error" in text:
            return ErrorCategory.SYNTAX.value, ""
        if "panic:" in text:
            return ErrorCategory.PANIC.value, ""
        if "--- FAIL" in output:
            return ErrorCategory.ASSERTION.value, ""
        return ErrorCategory.UNKNOWN.value, ""

    def _default_tool_name(self) -> str:
        return "go test"

    # Internal helpers -------------------------------------------------

    def _ensure_parser(self):
        if self._parser is not None:
            return
        try:
            from tree_sitter import Parser  # type: ignore[import-not-found]
            from tree_sitter_languages import get_language  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "Go backend requires 'tree_sitter' and 'tree_sitter_languages' packages"
            ) from exc

        self._parser = Parser()
        self._parser.set_language(get_language("go"))

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

        package_context = self._package_context(path)
        imports = self._collect_imports(path)

        # --- Infer branch coverage from control-flow analysis ---
        exec_branches_list, miss_branches_list = infer_branches(
            path, executed_lines, missing_lines
        )
        all_missing_branches = set(
            (frm, to) for frm, to in miss_branches_list
        )

        # Include branch source/dest lines in lines_of_interest
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

            # For large type declarations, try to find a smaller enclosing element
            if node.type == "type_declaration" and (end - begin) > line_limit:
                inner = self._find_enclosing_node(node, line)
                if inner is not None and inner is not node:
                    begin = inner.start_point[0] + 1
                    end = inner.end_point[0] + 1

            claimed_lines.update(range(begin, end))

            name = self._node_name(node, source_bytes)
            line_range = set(range(begin, end))

            # Collect branches relevant to this segment
            seg_missing_branches = {
                (frm, to) for frm, to in all_missing_branches
                if frm in line_range
            }

            # Build context: package line + receiver type definition if method
            context = list(package_context)
            receiver_ctx = self._get_receiver_context(node, source_bytes, tree)
            if receiver_ctx:
                context.extend(receiver_ctx)

            segments.append(
                CodeSegment(
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
            )

        return segments

    def _get_receiver_context(
        self, node, source_bytes: bytes, tree
    ) -> list[tuple[int, int]]:
        """If *node* is a method_declaration, return line ranges for its receiver type definition."""
        if node.type != "method_declaration":
            return []

        type_name = extract_receiver_type(node, source_bytes)
        if not type_name:
            return []

        # Find the type definition in the same file
        type_def_text = find_type_definition(tree.root_node, source_bytes, type_name)
        if not type_def_text:
            return []

        # Find the actual line range of the type definition in the file
        for child in tree.root_node.children:
            if child.type == "type_declaration":
                for spec in child.children:
                    if spec.type == "type_spec":
                        n = spec.child_by_field_name("name")
                        if n and source_bytes[n.start_byte:n.end_byte].decode("utf-8") == type_name:
                            begin = child.start_point[0] + 1
                            end = child.end_point[0] + 2  # +2 for range style
                            return [(begin, end)]
        return []

    def _find_enclosing_node(self, node, line: int):
        """Find the nearest enclosing declaration node for a given line.

        Supports function/method declarations as well as type, var, and const
        declarations so that struct definitions, interface definitions, and
        package-level variables are correctly segmented."""
        for child in node.children:
            start = child.start_point[0] + 1
            end = child.end_point[0] + 1
            if start <= line <= end:
                if child.type in {
                    "function_declaration",
                    "method_declaration",
                    "type_declaration",
                    "var_declaration",
                    "const_declaration",
                }:
                    return child
                result = self._find_enclosing_node(child, line)
                if result is not None:
                    return result
        return None

    # Keep old name as alias for backwards compatibility
    _find_enclosing_function = _find_enclosing_node

    def _node_name(self, node, source: bytes) -> str:
        name_field = node.child_by_field_name("name")
        if name_field is not None:
            return source[name_field.start_byte : name_field.end_byte].decode("utf-8")
        return "<anonymous>"

    def _package_pattern(self, package_dir: Path) -> str:
        try:
            rel = package_dir.relative_to(self.module_root)
        except ValueError:
            rel = Path('.')
        if not rel.parts:
            return "./"
        return "./" + "/".join(rel.parts)

    def _make_header(
        self,
        segment: CodeSegment,
        *,
        asked: dict | None,
        gained: dict | None,
        include_comments: bool = True,
    ) -> str:
        if not include_comments:
            return ""
        return (
            f"// file: {segment.identify()}\n"
            f"// asked: {json.dumps(asked if asked is not None else {})}\n"
            f"// gained: {json.dumps(gained if gained is not None else {})}\n\n"
        )

    def _package_context(self, path: Path) -> list[tuple[int, int]]:
        return [(1, 2)]

    def _collect_imports(self, path: Path) -> list[str]:
        imports: list[str] = []
        lines = path.read_text().splitlines(keepends=True)
        buffer: list[str] = []
        in_block = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import "):
                buffer.append(line)
                if stripped.endswith("("):
                    in_block = True
                else:
                    imports.extend(buffer)
                    buffer.clear()
            elif in_block:
                buffer.append(line)
                if stripped == ")":
                    in_block = False
                    imports.extend(buffer)
                    buffer.clear()
            elif buffer:
                imports.extend(buffer)
                buffer.clear()

        if buffer:
            imports.extend(buffer)

        return imports

    def _detect_module_path(self) -> str | None:
        gomod = self.module_root / "go.mod"
        if not gomod.exists():
            return None

        try:
            with gomod.open("r", encoding="utf-8") as fh:
                for line in fh:
                    stripped = line.strip()
                    if stripped.startswith("module "):
                        return stripped.split()[1]
        except OSError:
            return None

        return None

    def _cleanup_temp_tests(self, package_dir: Path) -> None:
        for tmp in package_dir.glob("coverup_tmp_*.go"):
            try:
                tmp.unlink()
            except OSError:
                continue

    def _ensure_unique_test_names(self, package_dir: Path, code: str) -> str:
        """Rename test functions AND helper types/functions to avoid
        redeclaration conflicts with existing *_test.go files in the
        same package."""
        # Patterns we need to dedup:
        #   func TestXxx(...)   – test functions
        #   func helperXxx(...) – non-test top-level functions
        #   type FooBar struct  – type declarations
        test_func_pat = re.compile(r"(\bfunc\s+)(Test\w+)")
        helper_func_pat = re.compile(r"(\bfunc\s+)([a-z]\w*)\s*\(")
        type_pat = re.compile(r"(\btype\s+)(\w+)\s+(?:struct|interface)")

        existing_funcs: set[str] = set()
        existing_types: set[str] = set()

        for file_path in package_dir.glob("*_test.go"):
            if file_path.name.startswith("coverup_tmp_"):
                continue
            try:
                text = file_path.read_text()
            except OSError:
                continue
            for match in test_func_pat.finditer(text):
                existing_funcs.add(match.group(2))
            for match in helper_func_pat.finditer(text):
                existing_funcs.add(match.group(2))
            for match in type_pat.finditer(text):
                existing_types.add(match.group(2))

        assigned_funcs: set[str] = set()
        assigned_types: set[str] = set()

        def _make_unique(name: str, existing: set[str], assigned: set[str]) -> str:
            new_name = name
            counter = 1
            while new_name in existing or new_name in assigned:
                suffix = "_CoverUp" if counter == 1 else f"_CoverUp{counter}"
                new_name = f"{name}{suffix}"
                counter += 1
            assigned.add(new_name)
            return new_name

        # 1. Rename test functions
        def repl_test(match: re.Match) -> str:
            prefix, name = match.groups()
            return f"{prefix}{_make_unique(name, existing_funcs, assigned_funcs)}"
        code = test_func_pat.sub(repl_test, code)

        # 2. Collect helper function names defined in this code
        local_helpers: dict[str, str] = {}  # old_name -> new_name
        for match in helper_func_pat.finditer(code):
            name = match.group(2)
            if name in existing_funcs and name not in local_helpers:
                new_name = _make_unique(name, existing_funcs, assigned_funcs)
                local_helpers[name] = new_name

        # 3. Collect type names defined in this code
        local_types: dict[str, str] = {}  # old_name -> new_name
        for match in type_pat.finditer(code):
            name = match.group(2)
            if name in existing_types and name not in local_types:
                new_name = _make_unique(name, existing_types, assigned_types)
                local_types[name] = new_name

        # 4. Apply renames (whole-word replacement)
        for old, new in {**local_helpers, **local_types}.items():
            code = re.sub(rf'\b{re.escape(old)}\b', new, code)

        return code

    def _format_with_goimports(
        self, path: Path, log_write: T.Callable[[str], None] | None
    ) -> bool:
        formatter_cmd: list[str] | None = None
        if self._goimports_cmd:
            formatter_cmd = [self._goimports_cmd, "-w", path.as_posix()]
        elif self._gofmt_cmd:
            formatter_cmd = [self._gofmt_cmd, "-w", path.as_posix()]

        if formatter_cmd is None:
            return True

        try:
            result = subprocess.run(
                formatter_cmd,
                cwd=self.module_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        except OSError as exc:  # pragma: no cover - diagnostic path
            if log_write:
                log_write(f"[coverup] failed to invoke {formatter_cmd[0]}: {exc}\n")
            return False

        if result.returncode != 0 and log_write:
            self._log_block(
                log_write,
                f"[coverup] {formatter_cmd[0]} exited with {result.returncode}:",
                result.stdout,
            )

        return result.returncode == 0

    def _package_name_for(self, path: Path) -> str | None:
        cached = self._package_cache.get(path)
        if cached is not None:
            return cached

        try:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    match = re.match(r"\s*package\s+([A-Za-z0-9_]+)", line)
                    if match:
                        name = match.group(1)
                        self._package_cache[path] = name
                        return name
        except OSError:
            return None

        return None

    def _prepare_test_code(self, test_code: str, segment: CodeSegment) -> str:
        package_name = self._package_name_for(segment.path)
        if not package_name:
            return test_code

        lines = test_code.splitlines()
        trailing_newline = test_code.endswith("\n")

        insertion_index = None
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
                continue
            if stripped.startswith("package "):
                current = stripped.split()[1]
                if current != package_name:
                    prefix = line[: line.find("package")]
                    lines[idx] = f"{prefix}package {package_name}"
                insertion_index = idx
                break
            insertion_index = idx
            lines.insert(idx, f"package {package_name}")
            break

        if insertion_index is None:
            lines.append(f"package {package_name}")

        result = "\n".join(lines)
        if trailing_newline and not result.endswith("\n"):
            result += "\n"
        return result

    def _run_go_mod_tidy(self, log_write: T.Callable[[str], None] | None) -> None:
        cmd = [self._go_cmd, "mod", "tidy"]
        try:
            subprocess.run(
                cmd,
                cwd=self.module_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True
            )
            if log_write:
                log_write("[coverup] 'go mod tidy' completed successfully.\n")
        except subprocess.CalledProcessError as e:
            if log_write:
                log_write(f"[coverup] 'go mod tidy' failed:\n{e.stdout}\n")

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

    def _summarize_go_test_failure(self, output: str) -> str:
        """Extract the most useful error lines from a failed ``go test``
        run.  Returns multiple lines when available so that the caller
        (and ultimately the LLM) gets actionable compile-error detail."""
        lines = output.splitlines()
        summary_parts: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Skip the unhelpful wrapper produced by TestDeadcodeElimination etc.
            if 'could not compile test program' in stripped:
                continue
            if any(m in stripped for m in (
                'undefined:', 'cannot ', 'imported and not used',
                'syntax error', 'too many', 'not enough',
                'does not implement', 'cannot use', 'redeclared',
                'duplicate ', 'not a type', 'invalid ', 'missing ',
                'panic:',
            )):
                summary_parts.append(stripped)
        if summary_parts:
            return '\n'.join(summary_parts[:20])
        # Fallback: first non-empty line
        for line in lines:
            stripped = line.strip()
            if stripped:
                return stripped
        return ""


def parse_go_cover_profile(
    profile_path: Path,
    *,
    module_root: Path | None = None,
    module_path: str | None = None,
) -> dict:
    with open(profile_path, "r", encoding="utf-8") as profile:
        lines = profile.readlines()

    if not lines:
        return {"files": {}, "meta": {"branch_coverage": False}, "summary": {}}

    mode_line = lines[0].strip()
    mode = mode_line.split(":", 1)[1].strip() if mode_line.startswith("mode:") else "count"

    files: dict[str, dict] = {}
    total_executed = 0
    total_missing = 0
    total_exec_branches = 0
    total_miss_branches = 0

    for entry in lines[1:]:
        entry = entry.strip()
        if not entry:
            continue

        try:
            location, statements_str, count_str = entry.rsplit(" ", 2)
        except ValueError:
            continue

        filepath, span = location.split(":", 1)
        start_str, end_str = span.split(",", 1)
        start_line = int(start_str.split(".")[0])
        end_line = int(end_str.split(".")[0])
        if end_line < start_line:
            end_line = start_line
        count = int(count_str)

        file_path = Path(filepath)

        if not file_path.is_absolute() and module_root is not None:
            file_path = (module_root / file_path).resolve()

        if not file_path.exists() and module_root is not None and module_path and filepath.startswith(module_path):
            relative = filepath[len(module_path) :].lstrip("/")
            candidate = (module_root / relative).resolve()
            if candidate.exists():
                file_path = candidate

        if not file_path.exists():
            # Skip entries that we cannot map to actual files.
            continue

        file_key = str(file_path)
        info = files.setdefault(
            file_key,
            {
                "executed_lines": set(),
                "missing_lines": set(),
                "executed_branches": [],
                "missing_branches": [],
            },
        )

        line_range = set(range(start_line, end_line + 1))
        if count > 0:
            info["executed_lines"].update(line_range)
            info["missing_lines"].difference_update(line_range)
        else:
            info["missing_lines"].update(line_range - info["executed_lines"])

    for file_key, info in files.items():
        executed = sorted(info["executed_lines"])
        missing = sorted(info["missing_lines"])

        # --- Infer branch coverage from control-flow analysis ---
        file_path = Path(file_key)
        exec_br_list, miss_br_list = [], []
        if file_path.exists() and not file_path.name.endswith("_test.go"):
            try:
                exec_br_list, miss_br_list = infer_branches(
                    file_path, set(executed), set(missing)
                )
            except Exception:
                pass  # graceful degradation if inference fails

        total = len(executed) + len(missing)
        covered = len(executed)
        info["executed_lines"] = executed
        info["missing_lines"] = missing
        info["executed_branches"] = exec_br_list
        info["missing_branches"] = miss_br_list
        info["summary"] = {
            "covered_lines": covered,
            "missing_lines": len(missing),
            "covered_branches": len(exec_br_list),
            "missing_branches": len(miss_br_list),
            "percent_covered": (covered / total * 100.0) if total else 100.0,
        }

        total_executed += covered
        total_missing += len(missing)
        total_exec_branches += len(exec_br_list)
        total_miss_branches += len(miss_br_list)

    summary_total = total_executed + total_missing
    summary = {
        "covered_lines": total_executed,
        "missing_lines": total_missing,
        "covered_branches": total_exec_branches,
        "missing_branches": total_miss_branches,
        "percent_covered": (total_executed / summary_total * 100.0)
        if summary_total
        else 100.0,
    }

    return {
        "meta": {"branch_coverage": True, "mode": mode},
        "files": files,
        "summary": summary,
    }
