# file: src/flask/src/flask/sansio/scaffold.py:311-317
# asked: {"lines": [311, 312, 317], "branches": []}
# gained: {"lines": [311, 312, 317], "branches": []}

import pytest
import typing as t
from unittest.mock import Mock, patch

T_route = t.TypeVar("T_route", bound=t.Callable[..., t.Any])

class TestScaffoldPut:
    """Test cases for Scaffold.put method to achieve full coverage."""
    
    def test_put_method_calls_method_route_with_correct_arguments(self):
        """Test that put method calls _method_route with PUT method and provided arguments."""
        from flask.sansio.scaffold import Scaffold
        
        # Create a mock scaffold instance with required import_name
        scaffold = Scaffold(import_name="test_app")
        
        # Mock the _method_route method to track calls
        mock_method_route = Mock(return_value=lambda f: f)
        scaffold._method_route = mock_method_route
        
        # Mock _check_setup_finished to avoid NotImplementedError
        scaffold._check_setup_finished = Mock()
        
        # Define test rule and options
        test_rule = "/test"
        test_options = {"endpoint": "test_endpoint"}
        
        # Create a dummy route function
        def dummy_route():
            pass
        
        # Call the put method
        decorator = scaffold.put(test_rule, **test_options)
        result = decorator(dummy_route)
        
        # Verify _method_route was called with correct arguments
        mock_method_route.assert_called_once_with("PUT", test_rule, test_options)
        
        # Verify the decorator returns the function
        assert result is dummy_route
    
    def test_put_method_returns_decorator_that_wraps_function(self):
        """Test that put method returns a decorator that properly wraps the route function."""
        from flask.sansio.scaffold import Scaffold
        
        # Create a mock scaffold instance with required import_name
        scaffold = Scaffold(import_name="test_app")
        
        # Mock _method_route to return a simple identity decorator
        def mock_decorator(func):
            return func
        
        scaffold._method_route = Mock(return_value=mock_decorator)
        
        # Mock _check_setup_finished to avoid NotImplementedError
        scaffold._check_setup_finished = Mock()
        
        # Define test parameters
        test_rule = "/api/resource"
        test_options = {"strict_slashes": False}
        
        # Test function to be decorated
        def test_route_function():
            return "PUT response"
        
        # Apply the decorator
        decorator = scaffold.put(test_rule, **test_options)
        decorated_function = decorator(test_route_function)
        
        # Verify the function is properly wrapped
        assert decorated_function is test_route_function
        assert decorated_function() == "PUT response"
    
    def test_put_method_with_additional_options(self):
        """Test put method with various option combinations."""
        from flask.sansio.scaffold import Scaffold
        
        scaffold = Scaffold(import_name="test_app")
        scaffold._method_route = Mock(return_value=lambda f: f)
        
        # Mock _check_setup_finished to avoid NotImplementedError
        scaffold._check_setup_finished = Mock()
        
        # Test with multiple options
        test_rule = "/users/<int:id>"
        test_options = {
            "endpoint": "user_detail",
            "strict_slashes": True,
            "defaults": {"id": 1}
        }
        
        def test_func():
            pass
        
        decorator = scaffold.put(test_rule, **test_options)
        result = decorator(test_func)
        
        scaffold._method_route.assert_called_once_with("PUT", test_rule, test_options)
        assert result is test_func
