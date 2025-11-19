import abc
import argparse
import typing as T

from ..segment import CodeSegment


class LanguageBackend(abc.ABC):
    """Abstract interface implemented by language-specific backends."""

    def __init__(self, args: argparse.Namespace):
        self.args = args

    def prepare_environment(self) -> None:
        """Hook invoked before any processing begins."""
        return None

    def handle_missing_dependencies(
        self,
        segment: CodeSegment,
        test_code: str,
        log_write: T.Callable[[str], None] | None = None,
    ) -> bool:
        """Attempts to resolve any missing dependencies.

        Returns ``True`` if processing should continue; ``False`` otherwise.
        """
        return True

    @abc.abstractmethod
    def measure_suite_coverage(
        self,
        *,
        pytest_args: str = "",
        isolate_tests: bool = False,
        branch_coverage: bool = True,
        trace=None,
        raise_on_failure: bool = True,
    ) -> dict:
        """Measures coverage for the entire test suite."""

    @abc.abstractmethod
    async def measure_test_coverage(
        self,
        segment: CodeSegment,
        test_code: str,
        *,
        isolate_tests: bool,
        branch_coverage: bool,
        log_write: T.Callable[[str], None] | None,
    ) -> dict:
        """Measures coverage for an individual candidate test."""

    @abc.abstractmethod
    def extract_test_code(self, response_content: str) -> str | None:
        """Extracts a test code block from the LLM response."""

    @abc.abstractmethod
    def save_successful_test(
        self,
        segment: CodeSegment,
        test_code: str,
        asked: dict,
        gained: dict,
    ) -> T.Optional[str]:
        """Persists a successful test, returning the saved path as a string."""

    @abc.abstractmethod
    def get_missing_coverage(
        self,
        coverage: dict,
        *,
        line_limit: int,
    ) -> T.List[CodeSegment]:
        """Generates the list of missing-coverage segments."""

    def format_test_error(self, output: str) -> str:
        """Formats raw test output before presenting it to the model."""

        return output

    def initial_empty_coverage(self) -> dict:
        """Provides a synthetic zero-coverage snapshot when no baseline run exists."""

        return {
            "meta": {"branch_coverage": False},
            "files": {},
            "summary": {
                "covered_lines": 0,
                "missing_lines": 0,
                "covered_branches": 0,
                "missing_branches": 0,
                "percent_covered": 0.0,
            },
        }
