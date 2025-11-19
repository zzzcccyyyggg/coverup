# file: src/click/src/click/utils.py:32-33
# asked: {"lines": [32, 33], "branches": []}
# gained: {"lines": [32, 33], "branches": []}

import pytest
from click.utils import _posixify

def test_posixify_with_spaces():
    """Test _posixify with spaces in the name."""
    result = _posixify("hello world")
    assert result == "hello-world"

def test_posixify_with_multiple_spaces():
    """Test _posixify with multiple consecutive spaces."""
    result = _posixify("hello   world")
    assert result == "hello-world"

def test_posixify_with_tabs():
    """Test _posixify with tabs in the name."""
    result = _posixify("hello\tworld")
    assert result == "hello-world"

def test_posixify_with_mixed_whitespace():
    """Test _posixify with mixed whitespace characters."""
    result = _posixify("hello \t \n world")
    assert result == "hello-world"

def test_posixify_with_uppercase():
    """Test _posixify with uppercase letters."""
    result = _posixify("Hello World")
    assert result == "hello-world"

def test_posixify_with_leading_trailing_spaces():
    """Test _posixify with leading and trailing spaces."""
    result = _posixify("  hello world  ")
    assert result == "hello-world"

def test_posixify_empty_string():
    """Test _posixify with empty string."""
    result = _posixify("")
    assert result == ""

def test_posixify_single_word():
    """Test _posixify with single word."""
    result = _posixify("hello")
    assert result == "hello"
