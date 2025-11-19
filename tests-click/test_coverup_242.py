# file: src/click/src/click/testing.py:206-211
# asked: {"lines": [206, 207, 209, 210], "branches": []}
# gained: {"lines": [206, 207, 209, 210], "branches": []}

import pytest
import click
from click.testing import CliRunner, Result

def test_result_stdout_property_with_carriage_return():
    """Test that Result.stdout property correctly replaces CRLF with LF."""
    runner = CliRunner()
    stdout_bytes = b"Hello\r\nWorld\r\n"
    
    result = Result(
        runner=runner,
        stdout_bytes=stdout_bytes,
        stderr_bytes=b"",
        output_bytes=stdout_bytes,
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    stdout_str = result.stdout
    assert stdout_str == "Hello\nWorld\n"
    assert "\r\n" not in stdout_str

def test_result_stdout_property_with_decoding_error():
    """Test that Result.stdout property handles decoding errors with replace."""
    runner = CliRunner(charset='utf-8')
    # Create bytes that cannot be decoded as UTF-8
    stdout_bytes = b"Hello\x80World"
    
    result = Result(
        runner=runner,
        stdout_bytes=stdout_bytes,
        stderr_bytes=b"",
        output_bytes=stdout_bytes,
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    stdout_str = result.stdout
    # Should replace invalid byte with replacement character
    assert "Hello" in stdout_str
    assert "World" in stdout_str
    # The invalid byte should be replaced, not cause an exception

def test_result_stdout_property_with_different_charset():
    """Test that Result.stdout property works with different charsets."""
    runner = CliRunner(charset='latin-1')
    # Latin-1 can encode all bytes, so use some Latin-1 specific characters
    stdout_bytes = b"Hello\xe9World\r\n"
    
    result = Result(
        runner=runner,
        stdout_bytes=stdout_bytes,
        stderr_bytes=b"",
        output_bytes=stdout_bytes,
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    stdout_str = result.stdout
    assert stdout_str == "HelloéWorld\n"
    assert "\r\n" not in stdout_str
