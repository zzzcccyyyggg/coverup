# file: src/flask/src/flask/cli.py:229-232
# asked: {"lines": [229, 230, 231, 232], "branches": []}
# gained: {"lines": [229, 230, 231], "branches": []}

import pytest
import typing as t
from flask import Flask
from flask.cli import locate_app

def test_locate_app_overload_true():
    """Test the overload signature with raise_if_not_found=True"""
    # This test verifies that the overload signature exists and can be imported
    # The actual implementation is tested elsewhere, but this ensures the overload is accessible
    
    # Verify the function signature matches the expected overload
    import inspect
    sig = inspect.signature(locate_app)
    assert 'module_name' in sig.parameters
    assert 'app_name' in sig.parameters
    assert 'raise_if_not_found' in sig.parameters
    
    # Check that the overload annotation exists in the function's annotations
    assert hasattr(locate_app, '__annotations__')
    annotations = locate_app.__annotations__
    assert 'return' in annotations
    
    # The actual return type annotation is 'Flask | None' for the combined function,
    # but the specific overload we're testing returns Flask
    # We verify that Flask is part of the return type annotation
    assert 'Flask' in str(annotations['return'])
    
    # The specific overload with raise_if_not_found=True should return Flask
    # This is a type-level test, so we mainly verify the function exists and is callable
    assert callable(locate_app)
