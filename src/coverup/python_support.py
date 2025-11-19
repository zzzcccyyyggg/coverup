import os
import re
import subprocess
import sys
import typing as T
from pathlib import Path


test_seq: int = 1
module_available: dict[str, int] = {}


def test_file_path(args, seq: int) -> Path:
    """Returns the Path for a test's file, given its sequence number."""

    return args.tests_dir / f"test_{args.prefix}_{seq}.py"


def new_test_file(args) -> Path:
    """Creates a new test file, returning its Path."""

    global test_seq

    while True:
        path = test_file_path(args, test_seq)
        if not (path.exists() or (path.parent / ("disabled_" + path.name)).exists()):
            try:
                path.touch(exist_ok=False)
                return path
            except FileExistsError:
                pass

        test_seq += 1


def clean_error(error: str) -> str:
    """Conservatively removes pytest-generated (and similar) output."""

    if (
        match := re.search(
            r"=====+ (?:FAILURES|ERRORS) ===+\n"
            r"___+ [^\n]+ _+___\n"
            r"\n?"
            r"(.*)",
            error,
            re.DOTALL,
        )
    ):
        error = match.group(1)

    if (
        match := re.search(
            r"(.*\n)"
            r"===+ short test summary info ===+",
            error,
            re.DOTALL,
        )
    ):
        error = match.group(1)

    return error


def find_imports(python_code: str) -> T.List[str]:
    """Collects a list of packages needed by examining 'import' statements."""

    import ast

    try:
        tree = ast.parse(python_code)
    except SyntaxError:
        return []

    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if isinstance(alias, ast.alias):
                    modules.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.append(node.module.split(".")[0])

    return [module for module in modules if module != "__main__"]


def missing_imports(modules: T.List[str]) -> T.List[str]:
    """Finds which modules are missing from the environment."""

    import importlib.util

    for module in modules:
        if module not in module_available:
            spec = importlib.util.find_spec(module)
            module_available[module] = 0 if spec is None else 1

    return [module for module in modules if not module_available[module]]


def install_missing_imports(
    args,
    segment,
    modules: T.List[str],
    *,
    logger: T.Callable[[str], None] | None = None,
) -> bool:
    """Attempts to install the given modules via pip."""

    import importlib.metadata

    all_ok = True

    for module in modules:
        try:
            proc = subprocess.run(
                (f"{sys.executable} -m pip install {module}").split(),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=60,
            )
            version = importlib.metadata.version(module)
            module_available[module] = 2

            message = f"Installed module {module} {version}"
            print(message)
            if logger:
                logger(message)

            if args.write_requirements_to:
                with args.write_requirements_to.open("a") as req:
                    req.write(f"{module}=={version}\n")
        except subprocess.CalledProcessError as exc:
            all_ok = False
            msg = str(exc.stdout, "UTF-8", errors="ignore") if exc.stdout else str(exc)
            if logger:
                logger(f"Unable to install module {module}:\n{msg}")

    return all_ok


def get_required_modules() -> T.List[str]:
    """Returns the list of modules that remain missing."""

    return [module for module in module_available if not module_available[module]]


def add_to_pythonpath(directory: Path) -> None:
    """Adds the given directory to PYTHONPATH for the current process."""

    os.environ["PYTHONPATH"] = str(directory) + (
        f":{os.environ['PYTHONPATH']}"
        if "PYTHONPATH" in os.environ
        else ""
    )
    sys.path.insert(0, str(directory))


def extract_python(response: str) -> str:
    """Extracts a Python code block from an LLM response."""

    match = re.search(r"```python\n(.*?)(?:```|\Z)", response, re.DOTALL)
    if not match:
        raise RuntimeError("Unable to extract Python code from response")
    return match.group(1)
