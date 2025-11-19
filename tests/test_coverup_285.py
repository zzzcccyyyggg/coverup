# file: src/flask/src/flask/sansio/scaffold.py:459-484
# asked: {"lines": [483, 484], "branches": []}
# gained: {"lines": [483, 484], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

def test_before_request_registration(monkeypatch):
    """Test that before_request decorator properly registers functions."""
    scaffold = Scaffold(__name__)
    
    # Mock the _check_setup_finished method to avoid NotImplementedError
    def mock_check_setup_finished(f_name):
        pass
    
    monkeypatch.setattr(scaffold, '_check_setup_finished', mock_check_setup_finished)
    
    # Define a simple before_request function
    @scaffold.before_request
    def before_request_func():
        return "test_value"
    
    # Verify the function was registered
    assert before_request_func in scaffold.before_request_funcs[None]
    assert len(scaffold.before_request_funcs[None]) == 1
    assert scaffold.before_request_funcs[None][0] is before_request_func

def test_before_request_returns_function(monkeypatch):
    """Test that before_request decorator returns the original function."""
    scaffold = Scaffold(__name__)
    
    # Mock the _check_setup_finished method to avoid NotImplementedError
    def mock_check_setup_finished(f_name):
        pass
    
    monkeypatch.setattr(scaffold, '_check_setup_finished', mock_check_setup_finished)
    
    def test_func():
        return "test"
    
    # Apply the decorator
    decorated_func = scaffold.before_request(test_func)
    
    # Verify the function is returned unchanged
    assert decorated_func is test_func
    assert decorated_func() == "test"
