# file: src/flask/src/flask/sansio/scaffold.py:327-333
# asked: {"lines": [327, 328, 333], "branches": []}
# gained: {"lines": [327, 328, 333], "branches": []}

import pytest
import typing as t
from unittest.mock import Mock, patch
from flask.sansio.scaffold import Scaffold

T_route = t.TypeVar("T_route", bound=t.Callable)

class TestScaffoldPatch:
    """Test cases for Scaffold.patch method to achieve full coverage."""
    
    def test_patch_method_calls_method_route_with_patch(self, monkeypatch):
        """Test that patch method calls _method_route with PATCH method."""
        # Create a mock Scaffold instance with required import_name
        scaffold = Scaffold(import_name="test_app")
        
        # Mock the _check_setup_finished method to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', Mock())
        
        # Mock the _method_route method to track calls
        mock_method_route = Mock(return_value=lambda f: f)
        monkeypatch.setattr(scaffold, '_method_route', mock_method_route)
        
        # Define a test rule and options
        test_rule = "/test/patch"
        test_options = {"endpoint": "test_patch_endpoint"}
        
        # Create a dummy route function
        def dummy_route():
            return "dummy response"
        
        # Call the patch method
        decorator = scaffold.patch(test_rule, **test_options)
        result = decorator(dummy_route)
        
        # Verify _method_route was called with correct arguments
        mock_method_route.assert_called_once_with("PATCH", test_rule, test_options)
        
        # Verify the decorator returns the function
        assert result is dummy_route
    
    def test_patch_method_returns_decorator(self):
        """Test that patch method returns a decorator function."""
        # Create a mock Scaffold instance with required import_name
        scaffold = Scaffold(import_name="test_app")
        
        # Mock _check_setup_finished to avoid NotImplementedError
        scaffold._check_setup_finished = Mock()
        
        # Mock _method_route to return a simple identity decorator
        def mock_method_route(method, rule, options):
            def decorator(f):
                return f
            return decorator
        
        scaffold._method_route = mock_method_route
        
        # Call patch and verify it returns a callable decorator
        decorator = scaffold.patch("/test")
        assert callable(decorator)
        
        # Test that the decorator works
        def test_func():
            return "test"
        
        decorated_func = decorator(test_func)
        assert decorated_func is test_func
