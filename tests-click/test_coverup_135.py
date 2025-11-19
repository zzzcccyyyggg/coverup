# file: src/click/src/click/testing.py:173-192
# asked: {"lines": [173, 183, 185, 186, 187, 188, 189, 190, 191, 192], "branches": []}
# gained: {"lines": [173, 183, 185, 186, 187, 188, 189, 190, 191, 192], "branches": []}

import pytest
import click
from click.testing import CliRunner, Result
from types import TracebackType

def test_result_init_with_exc_info():
    """Test Result.__init__ with exc_info parameter provided."""
    runner = CliRunner()
    stdout_bytes = b"stdout output"
    stderr_bytes = b"stderr output"
    output_bytes = b"mixed output"
    return_value = "test_return"
    exit_code = 0
    exception = None
    
    # Create a mock exception info
    try:
        raise ValueError("test exception")
    except ValueError as e:
        exc_info = (type(e), e, e.__traceback__)
    
    result = Result(
        runner=runner,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        output_bytes=output_bytes,
        return_value=return_value,
        exit_code=exit_code,
        exception=exception,
        exc_info=exc_info
    )
    
    assert result.runner is runner
    assert result.stdout_bytes == stdout_bytes
    assert result.stderr_bytes == stderr_bytes
    assert result.output_bytes == output_bytes
    assert result.return_value == return_value
    assert result.exit_code == exit_code
    assert result.exception is exception
    assert result.exc_info is exc_info

def test_result_init_without_exc_info():
    """Test Result.__init__ without exc_info parameter (default None)."""
    runner = CliRunner()
    stdout_bytes = b"stdout output"
    stderr_bytes = b"stderr output"
    output_bytes = b"mixed output"
    return_value = "test_return"
    exit_code = 1
    exception = None
    
    result = Result(
        runner=runner,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        output_bytes=output_bytes,
        return_value=return_value,
        exit_code=exit_code,
        exception=exception
        # exc_info defaults to None
    )
    
    assert result.runner is runner
    assert result.stdout_bytes == stdout_bytes
    assert result.stderr_bytes == stderr_bytes
    assert result.output_bytes == output_bytes
    assert result.return_value == return_value
    assert result.exit_code == exit_code
    assert result.exception is exception
    assert result.exc_info is None

def test_result_init_with_exception_and_exc_info():
    """Test Result.__init__ with both exception and exc_info provided."""
    runner = CliRunner()
    stdout_bytes = b"stdout output"
    stderr_bytes = b"stderr output"
    output_bytes = b"mixed output"
    return_value = None
    exit_code = 2
    
    # Create a mock exception and exc_info
    try:
        raise RuntimeError("test runtime error")
    except RuntimeError as e:
        exception = e
        exc_info = (type(e), e, e.__traceback__)
    
    result = Result(
        runner=runner,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        output_bytes=output_bytes,
        return_value=return_value,
        exit_code=exit_code,
        exception=exception,
        exc_info=exc_info
    )
    
    assert result.runner is runner
    assert result.stdout_bytes == stdout_bytes
    assert result.stderr_bytes == stderr_bytes
    assert result.output_bytes == output_bytes
    assert result.return_value == return_value
    assert result.exit_code == exit_code
    assert result.exception is exception
    assert result.exc_info is exc_info
