# file: src/click/src/click/testing.py:224-226
# asked: {"lines": [224, 225, 226], "branches": []}
# gained: {"lines": [224, 225, 226], "branches": []}

import pytest
from click.testing import Result, CliRunner
from click import Command

def test_result_repr_with_exception():
    """Test Result.__repr__ when exception is present."""
    runner = CliRunner()
    exception = ValueError("test error")
    result = Result(
        runner=runner,
        stdout_bytes=b"",
        stderr_bytes=b"",
        output_bytes=b"",
        return_value=None,
        exit_code=1,
        exception=exception,
        exc_info=None
    )
    
    repr_str = repr(result)
    assert repr_str == "<Result ValueError('test error')>"

def test_result_repr_without_exception():
    """Test Result.__repr__ when exception is None."""
    runner = CliRunner()
    result = Result(
        runner=runner,
        stdout_bytes=b"",
        stderr_bytes=b"",
        output_bytes=b"",
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    repr_str = repr(result)
    assert repr_str == "<Result okay>"
