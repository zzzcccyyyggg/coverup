# file: src/flask/src/flask/sansio/blueprints.py:684-692
# asked: {"lines": [684, 685, 689, 690, 692], "branches": []}
# gained: {"lines": [684, 685, 689, 690, 692], "branches": []}

import pytest
from flask import Flask
from flask.sansio.blueprints import Blueprint

def test_app_url_defaults_registers_function():
    """Test that app_url_defaults registers a function to app.url_default_functions."""
    app = Flask(__name__)
    bp = Blueprint('test', __name__)
    
    # Track calls to record_once
    record_once_calls = []
    original_record_once = bp.record_once
    bp.record_once = lambda func: record_once_calls.append(func)
    
    # Define a test function to register
    def test_url_defaults(endpoint, values):
        values['test_param'] = 'test_value'
    
    # Register the function using app_url_defaults
    result = bp.app_url_defaults(test_url_defaults)
    
    # Verify the function was returned
    assert result is test_url_defaults
    
    # Verify record_once was called
    assert len(record_once_calls) == 1
    
    # Now simulate the blueprint registration by calling the recorded function
    # with a mock state that has an app with url_default_functions
    mock_app = type('MockApp', (), {'url_default_functions': {}})()
    mock_state = type('MockState', (), {'app': mock_app})()
    
    # Execute the recorded function
    record_once_calls[0](mock_state)
    
    # Verify the function was added to app.url_default_functions under None key
    assert None in mock_app.url_default_functions
    assert len(mock_app.url_default_functions[None]) == 1
    assert mock_app.url_default_functions[None][0] is test_url_defaults

def test_app_url_defaults_multiple_functions():
    """Test that multiple app_url_defaults functions can be registered."""
    app = Flask(__name__)
    bp = Blueprint('test', __name__)
    
    # Track calls to record_once
    record_once_calls = []
    original_record_once = bp.record_once
    bp.record_once = lambda func: record_once_calls.append(func)
    
    # Define multiple test functions
    def test_url_defaults1(endpoint, values):
        values['param1'] = 'value1'
    
    def test_url_defaults2(endpoint, values):
        values['param2'] = 'value2'
    
    # Register both functions
    bp.app_url_defaults(test_url_defaults1)
    bp.app_url_defaults(test_url_defaults2)
    
    # Verify two calls to record_once
    assert len(record_once_calls) == 2
    
    # Simulate registration and verify both functions are added
    mock_app = type('MockApp', (), {'url_default_functions': {}})()
    mock_state = type('MockState', (), {'app': mock_app})()
    
    # Execute both recorded functions
    for func in record_once_calls:
        func(mock_state)
    
    # Verify both functions were added to the same list under None key
    assert None in mock_app.url_default_functions
    assert len(mock_app.url_default_functions[None]) == 2
    assert mock_app.url_default_functions[None][0] is test_url_defaults1
    assert mock_app.url_default_functions[None][1] is test_url_defaults2

def test_app_url_defaults_with_existing_functions():
    """Test app_url_defaults when url_default_functions already has entries."""
    app = Flask(__name__)
    bp = Blueprint('test', __name__)
    
    # Track calls to record_once
    record_once_calls = []
    original_record_once = bp.record_once
    bp.record_once = lambda func: record_once_calls.append(func)
    
    # Define existing function
    existing_func = lambda endpoint, values: None
    
    # Define new function to register
    def new_url_defaults(endpoint, values):
        values['new_param'] = 'new_value'
    
    # Register the new function
    bp.app_url_defaults(new_url_defaults)
    
    # Simulate registration with existing functions
    mock_app = type('MockApp', (), {'url_default_functions': {None: [existing_func]}})()
    mock_state = type('MockState', (), {'app': mock_app})()
    
    # Execute the recorded function
    record_once_calls[0](mock_state)
    
    # Verify the new function was appended to existing list
    assert len(mock_app.url_default_functions[None]) == 2
    assert mock_app.url_default_functions[None][0] is existing_func
    assert mock_app.url_default_functions[None][1] is new_url_defaults
