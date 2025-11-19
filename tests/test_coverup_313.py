# file: src/flask/src/flask/sansio/blueprints.py:613-621
# asked: {"lines": [618, 619, 621], "branches": []}
# gained: {"lines": [618, 619, 621], "branches": []}

import pytest
from flask import Flask
from flask.sansio.blueprints import Blueprint

def test_blueprint_before_app_request_registers_function():
    """Test that before_app_request registers a function to run before every app request."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    # Track if the function was called
    called = []
    
    @bp.before_app_request
    def before_request_func():
        called.append(True)
    
    # Manually call the deferred functions to simulate blueprint registration
    # This avoids the CLI attribute error in the full registration process
    state = bp.make_setup_state(app, {}, first_registration=True)
    for deferred in bp.deferred_functions:
        deferred(state)
    
    # Verify the function was registered in the app's before_request_funcs
    assert None in app.before_request_funcs
    assert before_request_func in app.before_request_funcs[None]
    
    # Verify the function is called during request processing
    @app.route('/test')
    def test_route():
        return 'ok'
    
    with app.test_client() as client:
        client.get('/test')
        assert len(called) == 1
        assert called[0] is True

def test_blueprint_before_app_request_returns_function():
    """Test that before_app_request returns the decorated function."""
    bp = Blueprint('test_bp', __name__)
    
    def test_func():
        pass
    
    decorated_func = bp.before_app_request(test_func)
    
    assert decorated_func is test_func
