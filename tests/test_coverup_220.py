# file: src/flask/src/flask/sansio/scaffold.py:284-293
# asked: {"lines": [284, 290, 291, 293], "branches": [[290, 291], [290, 293]]}
# gained: {"lines": [284, 290, 291, 293], "branches": [[290, 291], [290, 293]]}

import pytest
import typing as t
from unittest.mock import Mock, patch, MagicMock
from flask.sansio.scaffold import Scaffold

T_route = t.TypeVar("T_route", bound=t.Callable[..., t.Any])


class TestScaffoldMethodRoute:
    """Test cases for Scaffold._method_route method."""
    
    def test_method_route_with_methods_in_options_raises_type_error(self):
        """Test that _method_route raises TypeError when 'methods' is in options."""
        scaffold = Scaffold(__name__)
        
        with pytest.raises(TypeError, match="Use the 'route' decorator to use the 'methods' argument."):
            scaffold._method_route("GET", "/test", {"methods": ["GET"]})
    
    def test_method_route_successful_call(self):
        """Test that _method_route successfully calls route with correct parameters."""
        scaffold = Scaffold(__name__)
        
        # Create a mock function to be decorated
        def test_view():
            return "test response"
        
        # Mock the route method to capture its call and return a simple decorator
        with patch.object(scaffold, 'route') as mock_route:
            # Create a mock decorator that returns the function unchanged
            def mock_decorator(f):
                return f
            
            mock_route.return_value = mock_decorator
            
            # Call _method_route with some options
            decorator = scaffold._method_route("POST", "/test", {"endpoint": "test_endpoint"})
            
            # Apply the decorator to our test view
            decorated_view = decorator(test_view)
            
            # Verify route was called with correct parameters
            mock_route.assert_called_once_with("/test", methods=["POST"], endpoint="test_endpoint")
            
            # Verify the decorator returns the function (as per our mock implementation)
            assert decorated_view is test_view
    
    def test_method_route_with_empty_options(self):
        """Test that _method_route works with empty options dict."""
        scaffold = Scaffold(__name__)
        
        # Create a mock function to be decorated
        def test_view():
            return "test response"
        
        # Mock the route method
        with patch.object(scaffold, 'route') as mock_route:
            def mock_decorator(f):
                return f
            mock_route.return_value = mock_decorator
            
            # Call _method_route with empty options
            decorator = scaffold._method_route("PUT", "/empty", {})
            
            # Apply the decorator
            decorated_view = decorator(test_view)
            
            # Verify route was called with correct parameters
            mock_route.assert_called_once_with("/empty", methods=["PUT"])
            
            # Verify the decorator works
            assert decorated_view is test_view
    
    def test_method_route_with_multiple_options(self):
        """Test that _method_route passes multiple options correctly."""
        scaffold = Scaffold(__name__)
        
        # Create a mock function to be decorated
        def test_view():
            return "test response"
        
        # Mock the route method
        with patch.object(scaffold, 'route') as mock_route:
            def mock_decorator(f):
                return f
            mock_route.return_value = mock_decorator
            
            # Call _method_route with multiple options
            options = {
                "endpoint": "custom_endpoint",
                "defaults": {"id": 1},
                "strict_slashes": False
            }
            decorator = scaffold._method_route("DELETE", "/multi", options)
            
            # Apply the decorator
            decorated_view = decorator(test_view)
            
            # Verify route was called with correct parameters including all options
            mock_route.assert_called_once_with("/multi", methods=["DELETE"], endpoint="custom_endpoint", defaults={"id": 1}, strict_slashes=False)
            
            # Verify the decorator works
            assert decorated_view is test_view
