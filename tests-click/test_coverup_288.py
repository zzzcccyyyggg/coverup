# file: src/click/src/click/exceptions.py:294-295
# asked: {"lines": [294, 295], "branches": []}
# gained: {"lines": [294, 295], "branches": []}

import pytest
from click.exceptions import Abort


def test_abort_exception_creation():
    """Test that Abort exception can be created and has correct inheritance."""
    # Test basic creation
    abort = Abort()
    assert isinstance(abort, RuntimeError)
    assert isinstance(abort, Abort)
    assert str(abort) == ""
    
    # Test creation with message
    message = "Test abort message"
    abort_with_msg = Abort(message)
    assert isinstance(abort_with_msg, RuntimeError)
    assert isinstance(abort_with_msg, Abort)
    assert str(abort_with_msg) == message


def test_abort_exception_docstring():
    """Test that Abort exception has the correct docstring."""
    assert Abort.__doc__ == "An internal signalling exception that signals Click to abort."
