# file: src/flask/src/flask/sansio/scaffold.py:486-505
# asked: {"lines": [486, 487, 504, 505], "branches": []}
# gained: {"lines": [486, 487, 504, 505], "branches": []}

import pytest
from flask import Flask
from flask.blueprints import Blueprint

def test_after_request_registration():
    """Test that after_request decorator registers function correctly."""
    app = Flask(__name__)
    
    # Define a simple after_request function
    @app.after_request
    def add_header(response):
        response.headers['X-Test'] = 'test-value'
        return response
    
    # Verify the function was registered
    assert len(app.after_request_funcs[None]) == 1
    assert app.after_request_funcs[None][0] is add_header

def test_after_request_returns_function():
    """Test that after_request decorator returns the original function."""
    app = Flask(__name__)
    
    def my_after_request(response):
        return response
    
    # Apply the decorator and verify it returns the same function
    decorated_func = app.after_request(my_after_request)
    assert decorated_func is my_after_request

def test_after_request_multiple_registrations():
    """Test that multiple after_request functions can be registered."""
    app = Flask(__name__)
    
    @app.after_request
    def first_after_request(response):
        response.headers['First'] = '1'
        return response
    
    @app.after_request
    def second_after_request(response):
        response.headers['Second'] = '2'
        return response
    
    # Verify both functions were registered
    assert len(app.after_request_funcs[None]) == 2
    assert app.after_request_funcs[None][0] is first_after_request
    assert app.after_request_funcs[None][1] is second_after_request

def test_after_request_with_blueprint():
    """Test after_request registration with blueprint key."""
    bp = Blueprint('test', __name__)
    
    @bp.after_request
    def bp_after_request(response):
        response.headers['Blueprint'] = 'test'
        return response
    
    # Verify function was registered with None key (not blueprint name)
    assert len(bp.after_request_funcs[None]) == 1
    assert bp.after_request_funcs[None][0] is bp_after_request
