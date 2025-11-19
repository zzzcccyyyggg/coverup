# file: src/flask/src/flask/sansio/blueprints.py:633-641
# asked: {"lines": [633, 634, 638, 639, 641], "branches": []}
# gained: {"lines": [633, 634, 638, 639, 641], "branches": []}

import pytest
from flask.sansio.blueprints import Blueprint
from unittest.mock import Mock

def test_teardown_app_request_registers_function():
    """Test that teardown_app_request registers a function to be called after every request."""
    bp = Blueprint('test_bp', __name__)
    
    # Create a mock app with teardown_request_funcs
    mock_app = Mock()
    mock_app.teardown_request_funcs = {}
    
    # Track if the teardown function was registered
    registered_funcs = []
    
    def mock_record_once(func):
        # Simulate what happens when the blueprint is registered
        state = type('MockState', (), {'app': mock_app})()
        func(state)
        registered_funcs.append(func)
    
    # Monkey patch record_once to capture the registration
    bp.record_once = mock_record_once
    
    # Define a teardown function
    def teardown_func(error=None):
        return "teardown executed"
    
    # Register the teardown function
    result = bp.teardown_app_request(teardown_func)
    
    # Verify the function was returned
    assert result is teardown_func
    
    # Verify the function was registered in the app's teardown_request_funcs
    assert None in mock_app.teardown_request_funcs
    assert teardown_func in mock_app.teardown_request_funcs[None]
    assert len(registered_funcs) == 1

def test_teardown_app_request_multiple_functions():
    """Test that multiple teardown_app_request functions can be registered."""
    bp = Blueprint('test_bp', __name__)
    
    # Create a mock app with teardown_request_funcs
    mock_app = Mock()
    mock_app.teardown_request_funcs = {}
    
    def mock_record_once(func):
        state = type('MockState', (), {'app': mock_app})()
        func(state)
    
    bp.record_once = mock_record_once
    
    # Register multiple teardown functions
    def teardown_func1(error=None):
        return "teardown 1"
    
    def teardown_func2(error=None):
        return "teardown 2"
    
    result1 = bp.teardown_app_request(teardown_func1)
    result2 = bp.teardown_app_request(teardown_func2)
    
    # Verify both functions were returned
    assert result1 is teardown_func1
    assert result2 is teardown_func2
    
    # Verify both functions were registered
    assert None in mock_app.teardown_request_funcs
    assert teardown_func1 in mock_app.teardown_request_funcs[None]
    assert teardown_func2 in mock_app.teardown_request_funcs[None]
    assert len(mock_app.teardown_request_funcs[None]) == 2

def test_teardown_app_request_with_empty_dict():
    """Test teardown_app_request when teardown_request_funcs is initially empty."""
    bp = Blueprint('test_bp', __name__)
    
    # Create a mock app with empty teardown_request_funcs
    mock_app = Mock()
    mock_app.teardown_request_funcs = {}
    
    def mock_record_once(func):
        state = type('MockState', (), {'app': mock_app})()
        func(state)
    
    bp.record_once = mock_record_once
    
    def teardown_func(error=None):
        return "teardown executed"
    
    result = bp.teardown_app_request(teardown_func)
    
    # Verify the function was returned
    assert result is teardown_func
    
    # Verify the function was registered and list was created
    assert None in mock_app.teardown_request_funcs
    assert teardown_func in mock_app.teardown_request_funcs[None]
    assert isinstance(mock_app.teardown_request_funcs[None], list)
    assert len(mock_app.teardown_request_funcs[None]) == 1
