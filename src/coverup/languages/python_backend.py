import argparse
import json
import typing as T

from ..segment import CodeSegment, get_missing_coverage
from ..testrunner import measure_suite_coverage, measure_test_coverage
from ..python_support import (
    add_to_pythonpath,
    clean_error,
    extract_python,
    find_imports,
    install_missing_imports,
    missing_imports,
    new_test_file,
)

from .base import LanguageBackend
from ..diagnostic_ir import (
    DiagnosticIR, DiagnosticIRBuilder, ErrorCategory, Phase,
)


class PythonBackend(LanguageBackend):
    """Backend implementation targeting Python projects."""

    language_id = "python"

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

    def prepare_environment(self) -> None:
        if self.args.add_to_pythonpath:
            add_to_pythonpath(self.args.src_base_dir)

    def measure_suite_coverage(
        self,
        *,
        pytest_args: str = "",
        isolate_tests: bool = False,
        branch_coverage: bool = True,
        trace=None,
        raise_on_failure: bool = True,
    ) -> dict:
        return measure_suite_coverage(
            tests_dir=self.args.tests_dir,
            source_dir=self.args.package_dir,
            pytest_args=pytest_args,
            isolate_tests=isolate_tests,
            branch_coverage=branch_coverage,
            trace=trace,
            raise_on_failure=raise_on_failure,
        )

    async def measure_test_coverage(
        self,
        segment: CodeSegment,
        test_code: str,
        *,
        isolate_tests: bool,
        branch_coverage: bool,
        log_write: T.Callable[[str], None] | None,
    ) -> dict:
        pytest_args = (
            f"--count={self.args.repeat_tests} " if self.args.repeat_tests else ""
        ) + self.args.pytest_args
        return await measure_test_coverage(
            test=test_code,
            tests_dir=self.args.tests_dir,
            pytest_args=pytest_args,
            isolate_tests=isolate_tests,
            branch_coverage=branch_coverage,
            log_write=log_write,
        )

    def extract_test_code(self, response_content: str) -> str | None:
        if "```python" not in response_content:
            return None
        return extract_python(response_content)

    def handle_missing_dependencies(
        self,
        segment: CodeSegment,
        test_code: str,
        log_write: T.Callable[[str], None] | None = None,
    ) -> bool:
        missing = missing_imports(find_imports(test_code))
        if not missing:
            return True

        if log_write:
            log_write(f"Missing modules {' '.join(missing)}")

        if not self.args.install_missing_modules or not install_missing_imports(
            self.args,
            segment,
            missing,
            logger=(lambda msg: log_write(msg) if log_write else None),
        ):
            return False

        if log_write:
            log_write("Installed missing modules")
        return True

    def save_successful_test(
        self,
        segment: CodeSegment,
        test_code: str,
        asked: dict,
        gained: dict,
    ) -> T.Optional[str]:
        new_test = new_test_file(self.args)
        new_test.write_text(
            f"# file: {segment.identify()}\n"
            + f"# asked: {json.dumps(asked)}\n"
            + f"# gained: {json.dumps(gained)}\n\n"
            + test_code
        )
        return new_test.as_posix()

    def get_missing_coverage(
        self,
        coverage: dict,
        *,
        line_limit: int,
    ) -> T.List[CodeSegment]:
        return get_missing_coverage(coverage, line_limit=line_limit)

    def classify_error(self, output: str, phase: str = "run") -> DiagnosticIR:
        """Classify a Python test error into DiagnosticIR."""
        formatted = self.format_test_error(output)
        cat, code = self._classify_python_error(output)
        return (
            DiagnosticIRBuilder(language="python", phase=phase)
            .fail()
            .tool("pytest")
            .error(cat, code, formatted)
            .build()
        )

    @staticmethod
    def _classify_python_error(output: str) -> tuple:
        text = output.lower()
        if "importerror" in text or "modulenotfounderror" in text or "no module named" in text:
            return ErrorCategory.IMPORT.value, ""
        if "typeerror" in text:
            return ErrorCategory.TYPE.value, ""
        if "attributeerror" in text:
            return ErrorCategory.VISIBILITY.value, ""
        if "syntaxerror" in text:
            return ErrorCategory.SYNTAX.value, ""
        if "assertionerror" in text:
            return ErrorCategory.ASSERTION.value, ""
        if "nameerror" in text:
            return ErrorCategory.IMPORT.value, ""
        if "timeout" in text:
            return ErrorCategory.TIMEOUT.value, ""
        return ErrorCategory.UNKNOWN.value, ""

    def _default_tool_name(self) -> str:
        return "pytest"

    def format_test_error(self, output: str) -> str:
        return clean_error(output)
