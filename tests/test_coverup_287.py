# file: src/flask/src/flask/sansio/scaffold.py:507-539
# asked: {"lines": [538, 539], "branches": []}
# gained: {"lines": [538, 539], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

def test_teardown_request_registration(monkeypatch):
    """Test that teardown_request properly registers functions and returns the function."""
    scaffold = Scaffold(__name__)
    
    # Mock the _check_setup_finished method to avoid NotImplementedError
    def mock_check_setup_finished(f_name):
        pass
    
    monkeypatch.setattr(scaffold, '_check_setup_finished', mock_check_setup_finished)
    
    def teardown_func():
        pass
    
    # Register the teardown function
    result = scaffold.teardown_request(teardown_func)
    
    # Verify the function was added to the teardown_request_funcs dict
    assert teardown_func in scaffold.teardown_request_funcs[None]
    # Verify the function is returned
    assert result is teardown_func

def test_teardown_request_multiple_registrations(monkeypatch):
    """Test that multiple teardown_request functions can be registered."""
    scaffold = Scaffold(__name__)
    
    # Mock the _check_setup_finished method to avoid NotImplementedError
    def mock_check_setup_finished(f_name):
        pass
    
    monkeypatch.setattr(scaffold, '_check_setup_finished', mock_check_setup_finished)
    
    def teardown_func1():
        pass
    
    def teardown_func2():
        pass
    
    # Register multiple teardown functions
    result1 = scaffold.teardown_request(teardown_func1)
    result2 = scaffold.teardown_request(teardown_func2)
    
    # Verify both functions were added to the teardown_request_funcs dict
    assert teardown_func1 in scaffold.teardown_request_funcs[None]
    assert teardown_func2 in scaffold.teardown_request_funcs[None]
    # Verify both functions are returned
    assert result1 is teardown_func1
    assert result2 is teardown_func2
