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
from .base import LanguageBackend


class GoBackend(LanguageBackend):
    """Backend implementation targeting Go projects."""

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.module_root: Path = args.package_dir
        self._go_cmd = shutil.which("go") or "go"
        self._gofmt_cmd = shutil.which("gofmt")
        self._goimports_cmd = shutil.which("goimports")
        self._parser = None
        self._test_counter: dict[Path, int] = {}
        self._module_path = self._detect_module_path()
        self._package_cache: dict[Path, str] = {}

    def prepare_environment(self) -> None:
        if shutil.which(self._go_cmd) is None:
            raise RuntimeError(
                "Go executable not found. Ensure Go is installed and 'go' is on PATH."
            )

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
        temp_name = f"coverup_tmp_{os.getpid()}_{task_name}_{segment.begin}.go"
        temp_path = package_dir / temp_name

        self._cleanup_temp_tests(package_dir)
        header = self._make_header(segment, asked=None, gained=None, include_comments=False)
        prepared_code = self._prepare_test_code(test_code, segment)
        prepared_code = self._ensure_unique_test_names(package_dir, prepared_code)
        self._enforce_test_size(prepared_code, log_write)
        temp_path.write_text(header + prepared_code)
        formatted_ok = self._format_with_goimports(temp_path, log_write)

        fd, temp_name = tempfile.mkstemp(prefix="coverup-go-test-", suffix=".out")
        os.close(fd)
        profile_path = Path(temp_name)

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
            # Attempt to fix missing dependencies if that was the error
            if "no required module provides package" in output or "cannot find package" in output:
                if log_write:
                    log_write("[coverup] detected missing dependencies, attempting 'go mod tidy'...\n")
                self._run_go_mod_tidy(log_write)
                # We could retry the test here, but for now let's just let the error propagate
                # and rely on the next attempt or the user to re-run.
                # Actually, if we fixed it, we should probably retry immediately?
                # But the architecture here is simple, let's just tidy and fail,
                # so the next attempt (retry) might succeed.

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
            summary = self._summarize_go_test_failure(output)
            summary_line = summary or "go test failed; check the log above for details."
            message = f"{summary_line}\n(Full go test output truncated in log.)\n"
            raise subprocess.CalledProcessError(
                process.returncode, cmd, output=message.encode()
            )

        temp_path.unlink(missing_ok=True)

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
        return output

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

        segments: list[CodeSegment] = []
        claimed_lines: set[int] = set()
        lines_of_interest = set(missing_lines)

        for line in sorted(lines_of_interest):
            if line in claimed_lines:
                continue

            node = self._find_enclosing_function(tree.root_node, line)
            if node is None:
                continue

            begin = node.start_point[0] + 1
            end = node.end_point[0] + 1
            if end <= begin:
                end = begin + 1
            claimed_lines.update(range(begin, end))

            name = self._node_name(node, source_bytes)
            line_range = set(range(begin, end))
            segments.append(
                CodeSegment(
                    str(path),
                    name,
                    begin,
                    end,
                    lines_of_interest=lines_of_interest & line_range,
                    missing_lines=missing_lines & line_range,
                    executed_lines=executed_lines & line_range,
                    missing_branches=set(),
                    context=package_context,
                    imports=imports,
                )
            )

        return segments

    def _find_enclosing_function(self, node, line: int):
        for child in node.children:
            start = child.start_point[0] + 1
            end = child.end_point[0] + 1
            if start <= line <= end:
                if child.type in {"function_declaration", "method_declaration"}:
                    return child
                result = self._find_enclosing_function(child, line)
                if result is not None:
                    return result
        return None

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
        pattern = re.compile(r"(\bfunc\s+)(Test\w+)")
        existing: set[str] = set()

        for file_path in package_dir.glob("*_test.go"):
            if file_path.name.startswith("coverup_tmp_"):
                continue
            try:
                text = file_path.read_text()
            except OSError:
                continue
            for match in pattern.finditer(text):
                existing.add(match.group(2))

        assigned: set[str] = set()

        def repl(match: re.Match) -> str:
            prefix, name = match.groups()
            new_name = name
            counter = 1
            while new_name in existing or new_name in assigned:
                suffix = "_CoverUp" if counter == 1 else f"_CoverUp{counter}"
                new_name = f"{name}{suffix}"
                counter += 1
            assigned.add(new_name)
            return f"{prefix}{new_name}"

        return pattern.sub(repl, code)

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
        lines = output.splitlines()
        preferred = next((ln for ln in lines if ".go:" in ln), None)
        if preferred:
            return preferred.strip()
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
        total = len(executed) + len(missing)
        covered = len(executed)
        info["executed_lines"] = executed
        info["missing_lines"] = missing
        info["summary"] = {
            "covered_lines": covered,
            "missing_lines": len(missing),
            "covered_branches": 0,
            "missing_branches": 0,
            "percent_covered": (covered / total * 100.0) if total else 100.0,
        }

        total_executed += covered
        total_missing += len(missing)

    summary_total = total_executed + total_missing
    summary = {
        "covered_lines": total_executed,
        "missing_lines": total_missing,
        "covered_branches": 0,
        "missing_branches": 0,
        "percent_covered": (total_executed / summary_total * 100.0)
        if summary_total
        else 100.0,
    }

    return {
        "meta": {"branch_coverage": False, "mode": mode},
        "files": files,
        "summary": summary,
    }
