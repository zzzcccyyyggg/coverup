# file: src/click/src/click/testing.py:213-222
# asked: {"lines": [213, 214, 220, 221], "branches": []}
# gained: {"lines": [213, 214, 220, 221], "branches": []}

import pytest
import click
from click.testing import CliRunner, Result

def test_result_stderr_property_with_carriage_returns():
    """Test that stderr property correctly handles carriage returns and decoding."""
    runner = CliRunner(charset='utf-8')
    stderr_bytes = b"Error message with\r\ncarriage returns\r\nand newlines\n"
    
    result = Result(
        runner=runner,
        stdout_bytes=b"",
        stderr_bytes=stderr_bytes,
        output_bytes=b"",
        return_value=None,
        exit_code=1,
        exception=None,
        exc_info=None
    )
    
    stderr_str = result.stderr
    expected = "Error message with\ncarriage returns\nand newlines\n"
    assert stderr_str == expected

def test_result_stderr_property_with_decoding_error():
    """Test that stderr property handles decoding errors with 'replace' strategy."""
    runner = CliRunner(charset='utf-8')
    # Create bytes that cannot be decoded as UTF-8
    stderr_bytes = b"Normal text \xff\xfe followed by invalid UTF-8"
    
    result = Result(
        runner=runner,
        stdout_bytes=b"",
        stderr_bytes=stderr_bytes,
        output_bytes=b"",
        return_value=None,
        exit_code=1,
        exception=None,
        exc_info=None
    )
    
    stderr_str = result.stderr
    # Should replace invalid bytes with replacement character
    assert "Normal text" in stderr_str
    assert "\ufffd" in stderr_str  # Unicode replacement character

def test_result_stderr_property_with_different_charset():
    """Test that stderr property respects the runner's charset setting."""
    runner = CliRunner(charset='latin-1')
    # Latin-1 encoded text with special characters
    stderr_bytes = b"Error: caf\xe9 not found\r\n"
    
    result = Result(
        runner=runner,
        stdout_bytes=b"",
        stderr_bytes=stderr_bytes,
        output_bytes=b"",
        return_value=None,
        exit_code=1,
        exception=None,
        exc_info=None
    )
    
    stderr_str = result.stderr
    expected = "Error: café not found\n"
    assert stderr_str == expected

def test_result_stderr_property_mixed_line_endings():
    """Test that stderr property handles mixed line endings correctly."""
    runner = CliRunner(charset='utf-8')
    stderr_bytes = b"Line 1\r\nLine 2\nLine 3\r\n"
    
    result = Result(
        runner=runner,
        stdout_bytes=b"",
        stderr_bytes=stderr_bytes,
        output_bytes=b"",
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    stderr_str = result.stderr
    expected = "Line 1\nLine 2\nLine 3\n"
    assert stderr_str == expected
