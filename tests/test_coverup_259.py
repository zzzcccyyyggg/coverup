# file: src/flask/src/flask/sansio/blueprints.py:555-556
# asked: {"lines": [555, 556], "branches": []}
# gained: {"lines": [555, 556], "branches": []}

import pytest
import typing as t
from flask.sansio.blueprints import Blueprint

def test_app_template_global_overload_with_name():
    """Test the @t.overload decorator for app_template_global with name parameter."""
    bp = Blueprint('test', __name__)
    
    # This should call the overloaded method signature
    # We need to create a mock function to test the decorator behavior
    def mock_global_function():
        return "test_value"
    
    # Test the overloaded signature by calling app_template_global with a function
    # This should trigger the overload that returns the same function
    decorated_func = bp.app_template_global(mock_global_function)
    
    # Verify the function is returned unchanged (decorator behavior)
    assert decorated_func is mock_global_function
    assert decorated_func() == "test_value"

def test_app_template_global_overload_with_name_str():
    """Test the @t.overload decorator for app_template_global with string name parameter."""
    bp = Blueprint('test', __name__)
    
    # Test the overloaded signature by calling app_template_global with a string name
    # This should return a decorator function
    decorator = bp.app_template_global("custom_global")
    
    # Verify it returns a callable decorator
    assert callable(decorator)
    
    def mock_global_function():
        return "test_value"
    
    # Apply the decorator
    decorated_func = decorator(mock_global_function)
    
    # Verify the function is returned unchanged
    assert decorated_func is mock_global_function
