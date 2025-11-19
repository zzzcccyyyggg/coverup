# file: src/flask/src/flask/sansio/scaffold.py:295-301
# asked: {"lines": [301], "branches": []}
# gained: {"lines": [301], "branches": []}

import pytest
import typing as t
from flask.sansio.scaffold import Scaffold

T_route = t.TypeVar("T_route", bound=t.Callable[..., t.Any])

class TestScaffoldGetMethod:
    def test_get_method_route_called_correctly(self, monkeypatch):
        """Test that the get method calls _method_route with correct arguments."""
        scaffold = Scaffold("test_app")
        
        # Mock _check_setup_finished to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', lambda f_name: None)
        
        # Track calls to _method_route
        calls = []
        
        def mock_method_route(method, rule, options):
            calls.append((method, rule, options))
            # Return a simple decorator function
            def decorator(f):
                return f
            return decorator
        
        monkeypatch.setattr(scaffold, '_method_route', mock_method_route)
        
        # Call the get method
        def dummy_view():
            return "test"
        
        result = scaffold.get("/test", endpoint="test_endpoint")
        
        # Apply the decorator
        decorated_view = result(dummy_view)
        
        # Verify _method_route was called with correct arguments
        assert len(calls) == 1
        method, rule, options = calls[0]
        assert method == "GET"
        assert rule == "/test"
        assert "endpoint" in options
        assert options["endpoint"] == "test_endpoint"
        assert "methods" not in options  # Should not have methods in options
        
        # Verify the decorator returns a callable
        assert callable(result)
        assert decorated_view is dummy_view
        
    def test_get_method_with_methods_in_options_raises_error(self, monkeypatch):
        """Test that get method raises TypeError when methods is in options."""
        scaffold = Scaffold("test_app")
        
        # Mock _check_setup_finished to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', lambda f_name: None)
        
        def dummy_view():
            return "test"
        
        # This should raise TypeError because 'methods' should not be in options
        with pytest.raises(TypeError, match="Use the 'route' decorator to use the 'methods' argument."):
            result = scaffold.get("/test", methods=["GET"])
            result(dummy_view)
