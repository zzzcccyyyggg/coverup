# file: src/flask/src/flask/sansio/scaffold.py:435-457
# asked: {"lines": [435, 436, 453, 454, 455, 457], "branches": []}
# gained: {"lines": [435, 436, 453, 454, 455, 457], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffoldEndpoint:
    """Test cases for the Scaffold.endpoint method."""
    
    def test_endpoint_decorator_registers_view_function(self, monkeypatch):
        """Test that the endpoint decorator properly registers a view function."""
        scaffold = Scaffold(__name__)
        
        # Mock the _check_setup_finished method to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', lambda f_name: None)
        
        endpoint_name = "test_endpoint"
        
        # Use the endpoint decorator
        decorator = scaffold.endpoint(endpoint_name)
        
        # Define a test view function
        def test_view():
            return "test response"
        
        # Apply the decorator
        decorated_view = decorator(test_view)
        
        # Verify the view function was registered
        assert scaffold.view_functions[endpoint_name] is test_view
        # Verify the decorator returns the original function
        assert decorated_view is test_view
    
    def test_endpoint_decorator_multiple_registrations(self, monkeypatch):
        """Test that multiple endpoint decorators work correctly."""
        scaffold = Scaffold(__name__)
        
        # Mock the _check_setup_finished method to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', lambda f_name: None)
        
        # Register multiple endpoints
        endpoint1 = "endpoint1"
        endpoint2 = "endpoint2"
        
        decorator1 = scaffold.endpoint(endpoint1)
        decorator2 = scaffold.endpoint(endpoint2)
        
        def view1():
            return "view1"
        
        def view2():
            return "view2"
        
        # Apply decorators
        decorated1 = decorator1(view1)
        decorated2 = decorator2(view2)
        
        # Verify registrations
        assert scaffold.view_functions[endpoint1] is view1
        assert scaffold.view_functions[endpoint2] is view2
        assert decorated1 is view1
        assert decorated2 is view2
    
    def test_endpoint_decorator_overwrites_existing(self, monkeypatch):
        """Test that endpoint decorator overwrites existing endpoint registration."""
        scaffold = Scaffold(__name__)
        
        # Mock the _check_setup_finished method to avoid NotImplementedError
        monkeypatch.setattr(scaffold, '_check_setup_finished', lambda f_name: None)
        
        endpoint_name = "test_endpoint"
        
        # Register first view function
        decorator = scaffold.endpoint(endpoint_name)
        
        def first_view():
            return "first"
        
        decorated_first = decorator(first_view)
        assert scaffold.view_functions[endpoint_name] is first_view
        
        # Register second view function for same endpoint
        def second_view():
            return "second"
        
        decorated_second = decorator(second_view)
        
        # Verify the second view overwrote the first
        assert scaffold.view_functions[endpoint_name] is second_view
        assert decorated_second is second_view
