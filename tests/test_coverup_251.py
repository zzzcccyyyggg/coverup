# file: src/flask/src/flask/sansio/blueprints.py:643-653
# asked: {"lines": [643, 644, 650, 651, 653], "branches": []}
# gained: {"lines": [643, 644, 650, 651, 653], "branches": []}

import pytest
from flask.sansio.blueprints import Blueprint
from unittest.mock import Mock

def test_blueprint_app_context_processor_registers_function():
    """Test that app_context_processor registers a function to be called during blueprint registration."""
    bp = Blueprint('test_bp', __name__)
    
    # Track if the lambda function was called and what it does
    recorded_func = None
    
    def mock_record_once(func):
        nonlocal recorded_func
        recorded_func = func
        # Don't call the function yet, just record it
    
    # Monkeypatch record_once to track the call
    bp.record_once = mock_record_once
    
    # Define a context processor function
    def context_processor():
        return {'test_key': 'test_value'}
    
    # Register the context processor
    result = bp.app_context_processor(context_processor)
    
    # Verify the function was returned
    assert result is context_processor
    
    # Verify the lambda was recorded
    assert recorded_func is not None
    
    # Now simulate what happens during blueprint registration
    # Create a mock app with template_context_processors
    mock_app = Mock()
    mock_app.template_context_processors = {None: []}
    
    # Create a mock state object
    mock_state = Mock()
    mock_state.app = mock_app
    
    # Call the recorded function with the mock state
    recorded_func(mock_state)
    
    # Verify the function was added to app's template_context_processors
    assert context_processor in mock_app.template_context_processors[None]

def test_blueprint_app_context_processor_multiple_registrations():
    """Test that multiple app_context_processors can be registered."""
    bp = Blueprint('test_bp', __name__)
    
    recorded_funcs = []
    
    def mock_record_once(func):
        recorded_funcs.append(func)
    
    bp.record_once = mock_record_once
    
    # Register multiple context processors
    def processor1():
        return {'key1': 'value1'}
    
    def processor2():
        return {'key2': 'value2'}
    
    result1 = bp.app_context_processor(processor1)
    result2 = bp.app_context_processor(processor2)
    
    # Verify both functions were returned
    assert result1 is processor1
    assert result2 is processor2
    
    # Verify both were recorded
    assert len(recorded_funcs) == 2
    
    # Simulate registration for both
    mock_app = Mock()
    mock_app.template_context_processors = {None: []}
    mock_state = Mock()
    mock_state.app = mock_app
    
    for func in recorded_funcs:
        func(mock_state)
    
    # Verify both were added to app's template_context_processors
    assert processor1 in mock_app.template_context_processors[None]
    assert processor2 in mock_app.template_context_processors[None]

def test_blueprint_app_context_processor_with_setupmethod():
    """Test that app_context_processor respects the setupmethod decorator."""
    bp = Blueprint('test_bp', __name__)
    
    # Mock the _check_setup_finished method to track calls
    original_check = bp._check_setup_finished
    check_calls = []
    
    def mock_check_setup_finished(f_name):
        check_calls.append(f_name)
        original_check(f_name)
    
    bp._check_setup_finished = mock_check_setup_finished
    
    # Register a context processor
    def context_processor():
        return {}
    
    result = bp.app_context_processor(context_processor)
    
    # Verify _check_setup_finished was called with the correct function name
    # It should be called for app_context_processor, record_once, and record
    assert len(check_calls) == 3
    assert check_calls[0] == 'app_context_processor'
    assert check_calls[1] == 'record_once'
    assert check_calls[2] == 'record'
    
    # Verify the function was returned
    assert result is context_processor
