# file: src/flask/src/flask/sansio/scaffold.py:319-325
# asked: {"lines": [319, 320, 325], "branches": []}
# gained: {"lines": [319, 320, 325], "branches": []}

import pytest
import typing as t
from flask.sansio.scaffold import Scaffold

class TestScaffoldDelete:
    """Test cases for Scaffold.delete method to achieve full coverage."""
    
    def test_delete_method_route_call(self, monkeypatch):
        """Test that delete method calls _method_route with correct parameters."""
        scaffold = Scaffold(import_name='test_app')
        
        # Mock _check_setup_finished to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', lambda f_name: None)
        
        # Track the call to _method_route
        called_with = []
        def mock_method_route(method, rule, options):
            called_with.append((method, rule, options))
            return lambda f: f
        
        monkeypatch.setattr(scaffold, '_method_route', mock_method_route)
        
        # Call delete method
        @scaffold.delete('/test', endpoint='test_endpoint')
        def test_handler():
            return "test"
        
        # Verify _method_route was called with correct parameters
        assert len(called_with) == 1
        assert called_with[0][0] == 'DELETE'
        assert called_with[0][1] == '/test'
        assert called_with[0][2]['endpoint'] == 'test_endpoint'
    
    def test_delete_returns_decorator(self, monkeypatch):
        """Test that delete method returns a decorator function."""
        scaffold = Scaffold(import_name='test_app')
        
        # Mock _check_setup_finished to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', lambda f_name: None)
        
        # Mock _method_route to return a simple decorator
        def mock_method_route(method, rule, options):
            def decorator(f):
                return f
            return decorator
        
        monkeypatch.setattr(scaffold, '_method_route', mock_method_route)
        
        # Call delete method and verify it returns a decorator
        decorator = scaffold.delete('/test')
        assert callable(decorator)
        
        # Test that the decorator can be applied to a function
        def test_handler():
            return "test"
        
        decorated = decorator(test_handler)
        assert decorated == test_handler
