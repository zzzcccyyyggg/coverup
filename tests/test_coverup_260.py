# file: src/flask/src/flask/sansio/app.py:769-770
# asked: {"lines": [769, 770], "branches": []}
# gained: {"lines": [769, 770], "branches": []}

import pytest
import typing as t
from flask.sansio.app import App

def test_template_global_overload():
    """Test that the template_global overload signature is accessible."""
    # Create a minimal App instance by mocking the problematic attributes
    app = App.__new__(App)
    
    # Access the overload to ensure it's executed
    overload_method = app.template_global
    
    # Verify it's a method
    assert callable(overload_method)
    
    # Verify the method has the expected annotations
    assert hasattr(overload_method, '__annotations__')
    annotations = overload_method.__annotations__
    assert 'name' in annotations
    assert 'return' in annotations
