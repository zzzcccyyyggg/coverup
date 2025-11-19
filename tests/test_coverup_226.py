# file: src/flask/src/flask/debughelpers.py:17-20
# asked: {"lines": [17, 18], "branches": []}
# gained: {"lines": [17, 18], "branches": []}

import pytest
from flask.debughelpers import UnexpectedUnicodeError


def test_unexpected_unicode_error_inheritance():
    """Test that UnexpectedUnicodeError inherits from both AssertionError and UnicodeError."""
    error = UnexpectedUnicodeError("test message")
    
    # Verify inheritance hierarchy
    assert isinstance(error, AssertionError)
    assert isinstance(error, UnicodeError)
    assert isinstance(error, Exception)
    
    # Verify message is set correctly
    assert str(error) == "test message"


def test_unexpected_unicode_error_unicode_behavior():
    """Test UnicodeError specific behavior with UnexpectedUnicodeError."""
    # Test that it can handle unicode-related error scenarios
    try:
        raise UnexpectedUnicodeError("unicode error test")
    except UnicodeError as e:
        assert str(e) == "unicode error test"
        assert isinstance(e, UnexpectedUnicodeError)


def test_unexpected_unicode_error_assertion_behavior():
    """Test AssertionError specific behavior with UnexpectedUnicodeError."""
    # Test that it can be caught as an AssertionError
    try:
        raise UnexpectedUnicodeError("assertion error test")
    except AssertionError as e:
        assert str(e) == "assertion error test"
        assert isinstance(e, UnexpectedUnicodeError)
