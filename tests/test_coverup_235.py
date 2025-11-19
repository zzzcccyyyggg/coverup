# file: src/flask/src/flask/ctx.py:486-492
# asked: {"lines": [486, 492], "branches": []}
# gained: {"lines": [486, 492], "branches": []}

import pytest
from flask import Flask
from flask.ctx import AppContext
from types import TracebackType


def test_app_context_exit_with_exception():
    """Test that AppContext.__exit__ calls pop with the exception value."""
    app = Flask(__name__)
    ctx = AppContext(app)
    
    # Mock the pop method to verify it's called with the correct exception
    original_pop = ctx.pop
    called_with = None
    
    def mock_pop(exc):
        nonlocal called_with
        called_with = exc
    
    ctx.pop = mock_pop
    
    # Create a test exception
    test_exception = ValueError("test error")
    
    # Call __exit__ with the exception
    ctx.__exit__(ValueError, test_exception, None)
    
    # Verify pop was called with the exception value
    assert called_with is test_exception


def test_app_context_exit_without_exception():
    """Test that AppContext.__exit__ calls pop with None when no exception occurred."""
    app = Flask(__name__)
    ctx = AppContext(app)
    
    # Mock the pop method to verify it's called with None
    original_pop = ctx.pop
    called_with = None
    
    def mock_pop(exc):
        nonlocal called_with
        called_with = exc
    
    ctx.pop = mock_pop
    
    # Call __exit__ without an exception (normal exit)
    ctx.__exit__(None, None, None)
    
    # Verify pop was called with None
    assert called_with is None


def test_app_context_exit_with_exception_type_only():
    """Test that AppContext.__exit__ calls pop with None when only exception type is provided."""
    app = Flask(__name__)
    ctx = AppContext(app)
    
    # Mock the pop method to verify it's called with None
    original_pop = ctx.pop
    called_with = None
    
    def mock_pop(exc):
        nonlocal called_with
        called_with = exc
    
    ctx.pop = mock_pop
    
    # Call __exit__ with only exception type (no actual exception instance)
    ctx.__exit__(ValueError, None, None)
    
    # Verify pop was called with None
    assert called_with is None
