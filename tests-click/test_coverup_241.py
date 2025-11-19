# file: src/click/src/click/testing.py:194-204
# asked: {"lines": [194, 195, 202, 203], "branches": []}
# gained: {"lines": [194, 195, 202, 203], "branches": []}

import pytest
import click
from click.testing import CliRunner, Result

def test_result_output_property_with_carriage_return():
    """Test that Result.output property correctly replaces CRLF with LF."""
    runner = CliRunner(charset='utf-8')
    
    # Create a Result instance with output_bytes containing CRLF
    output_bytes = b"Hello\r\nWorld\r\nTest"
    result = Result(
        runner=runner,
        stdout_bytes=b"stdout",
        stderr_bytes=b"stderr", 
        output_bytes=output_bytes,
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    # Test that CRLF is replaced with LF
    expected_output = "Hello\nWorld\nTest"
    assert result.output == expected_output

def test_result_output_property_with_decoding_error():
    """Test that Result.output property handles decoding errors with 'replace'."""
    runner = CliRunner(charset='utf-8')
    
    # Create a Result instance with invalid UTF-8 bytes
    output_bytes = b"Hello\x80World"  # Invalid UTF-8 sequence
    result = Result(
        runner=runner,
        stdout_bytes=b"stdout",
        stderr_bytes=b"stderr",
        output_bytes=output_bytes,
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    # Test that invalid bytes are replaced with replacement character
    output = result.output
    assert "Hello" in output
    assert "World" in output
    # The invalid byte should be replaced, not cause an exception

def test_result_output_property_with_different_charset():
    """Test that Result.output property works with different charsets."""
    runner = CliRunner(charset='latin-1')
    
    # Create a Result instance with latin-1 encoded bytes
    output_bytes = b"Hello\xe9World\r\nTest"  # é character in latin-1
    result = Result(
        runner=runner,
        stdout_bytes=b"stdout",
        stderr_bytes=b"stderr",
        output_bytes=output_bytes,
        return_value=None,
        exit_code=0,
        exception=None,
        exc_info=None
    )
    
    # Test that latin-1 decoding works and CRLF is replaced
    expected_output = "HelloéWorld\nTest"
    assert result.output == expected_output
