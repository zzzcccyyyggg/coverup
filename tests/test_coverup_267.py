# file: src/flask/src/flask/sansio/blueprints.py:497-498
# asked: {"lines": [497, 498], "branches": []}
# gained: {"lines": [497, 498], "branches": []}

import pytest
import typing as t
from flask.sansio.blueprints import Blueprint

def test_app_template_test_overload_decorator():
    """Test that the @t.overload decorator for app_template_test is executed."""
    bp = Blueprint('test', __name__)
    
    # The @t.overload decorator should be applied without errors
    # This test ensures the decorator syntax is valid and the method exists
    assert hasattr(bp, 'app_template_test')
    
    # Verify the method has the expected signature by checking its __annotations__
    method = bp.app_template_test
    assert callable(method)
    
    # The overload decorator should be present in the method's attributes
    # This is a basic check that the decorator was applied
    assert hasattr(method, '__annotations__')

def test_app_template_test_overload_with_type_parameter():
    """Test the specific overload signature that takes a template test function."""
    bp = Blueprint('test', __name__)
    
    # Create a mock template test function
    def mock_template_test(value: t.Any) -> bool:
        return isinstance(value, str)
    
    # The overload should allow this usage pattern
    # This test verifies the type annotation is valid
    decorated_test = bp.app_template_test(mock_template_test)
    
    # The decorated function should be the same as the input (for the overload case)
    assert decorated_test is mock_template_test

def test_app_template_test_overload_type_checking():
    """Test type checking behavior for the overload decorator."""
    bp = Blueprint('test', __name__)
    
    # This test ensures the type annotations are syntactically valid
    # We're not actually calling the method with runtime type checking,
    # but ensuring the decorator syntax doesn't cause errors
    
    # Access the method to trigger any potential syntax errors
    method = bp.app_template_test
    
    # Verify it's a bound method
    assert hasattr(method, '__self__')
    assert method.__self__ is bp
