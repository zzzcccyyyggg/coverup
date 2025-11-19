# file: src/flask/src/flask/sansio/blueprints.py:623-631
# asked: {"lines": [623, 624, 628, 629, 631], "branches": []}
# gained: {"lines": [623, 624, 628, 629, 631], "branches": []}

import pytest
from flask import Flask
from flask.sansio.blueprints import Blueprint
from flask.sansio.blueprints import BlueprintSetupState

def test_after_app_request_registers_function():
    """Test that after_app_request registers a function to be called after every request."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    # Track if the function was called
    called = []
    
    @bp.after_app_request
    def after_request_func(response):
        called.append(True)
        return response
    
    # Create a mock setup state to test the deferred function
    state = BlueprintSetupState(bp, app, {}, True)
    
    # Execute the deferred functions
    for deferred in bp.deferred_functions:
        deferred(state)
    
    # Verify the function was added to the app's after_request_funcs
    assert None in app.after_request_funcs
    assert len(app.after_request_funcs[None]) == 1
    assert after_request_func in app.after_request_funcs[None]

def test_after_app_request_returns_function():
    """Test that after_app_request returns the decorated function."""
    bp = Blueprint('test_bp', __name__)
    
    def test_func(response):
        return response
    
    decorated_func = bp.after_app_request(test_func)
    
    assert decorated_func is test_func

def test_after_app_request_only_registered_once():
    """Test that after_app_request functions are only registered once even if blueprint setup state is created multiple times."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    call_count = 0
    
    @bp.after_app_request
    def after_request_func(response):
        nonlocal call_count
        call_count += 1
        return response
    
    # Create setup states with first_registration=True and first_registration=False
    state_first = BlueprintSetupState(bp, app, {}, True)
    state_second = BlueprintSetupState(bp, app, {}, False)
    
    # Execute deferred functions with first registration
    for deferred in bp.deferred_functions:
        deferred(state_first)
    
    # Execute deferred functions with second registration (should not register again)
    for deferred in bp.deferred_functions:
        deferred(state_second)
    
    # The function should only be in the list once
    assert None in app.after_request_funcs
    assert len(app.after_request_funcs[None]) == 1
    assert call_count == 0  # The function itself hasn't been called yet
