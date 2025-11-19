# file: src/flask/src/flask/cli.py:94-117
# asked: {"lines": [94, 102, 104, 105, 106, 108, 110, 113, 117], "branches": [[105, 106], [105, 113], [106, 108], [106, 110]]}
# gained: {"lines": [94, 102, 104, 105, 106, 108, 110, 113, 117], "branches": [[105, 106], [105, 113], [106, 108], [106, 110]]}

import pytest
import sys
import typing as t
from flask.app import Flask
from flask.cli import _called_with_wrong_args

def test_called_with_wrong_args_found_in_traceback():
    """Test _called_with_wrong_args returns False when function is found in traceback."""
    
    def test_function() -> Flask:
        raise TypeError("Test error")
    
    try:
        test_function()
    except TypeError:
        result = _called_with_wrong_args(test_function)
    
    assert result is False

def test_called_with_wrong_args_not_found_in_traceback():
    """Test _called_with_wrong_args returns True when function is not found in traceback."""
    
    def test_function() -> Flask:
        return Flask(__name__)
    
    def calling_function():
        try:
            test_function()
        except Exception:
            pass
    
    # Create a scenario where the function is not in the traceback
    def wrapper_function():
        try:
            calling_function()
        except Exception:
            pass
    
    try:
        wrapper_function()
    except Exception:
        pass
    
    # Now test with a different function that wasn't in the call chain
    def unrelated_function() -> Flask:
        return Flask(__name__)
    
    try:
        # This will raise TypeError but unrelated_function wasn't in the call chain
        raise TypeError("Test error")
    except TypeError:
        result = _called_with_wrong_args(unrelated_function)
    
    assert result is True

def test_called_with_wrong_args_with_none_traceback():
    """Test _called_with_wrong_args when there's no traceback (tb is None)."""
    
    def test_function() -> Flask:
        return Flask(__name__)
    
    # Mock sys.exc_info to return None for traceback
    original_exc_info = sys.exc_info
    
    def mock_exc_info():
        return (None, None, None)
    
    sys.exc_info = mock_exc_info
    
    try:
        result = _called_with_wrong_args(test_function)
        assert result is True
    finally:
        sys.exc_info = original_exc_info
