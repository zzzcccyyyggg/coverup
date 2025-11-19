# file: src/flask/src/flask/sansio/scaffold.py:583-595
# asked: {"lines": [583, 584, 594, 595], "branches": []}
# gained: {"lines": [583, 584, 594, 595], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

def test_url_defaults_registers_function(monkeypatch):
    """Test that url_defaults decorator registers the function correctly."""
    scaffold = Scaffold(__name__)
    
    # Mock the _check_setup_finished method to avoid NotImplementedError
    def mock_check_setup_finished(f_name):
        pass
    
    monkeypatch.setattr(scaffold, '_check_setup_finished', mock_check_setup_finished)
    
    # Define a test function to register
    def test_defaults(endpoint, values):
        values['test'] = 'value'
    
    # Register the function using the url_defaults decorator
    registered_func = scaffold.url_defaults(test_defaults)
    
    # Verify the function was registered in the correct location
    assert test_defaults in scaffold.url_default_functions[None]
    # Verify the decorator returns the original function
    assert registered_func is test_defaults

def test_url_defaults_multiple_functions(monkeypatch):
    """Test that multiple url_defaults functions can be registered."""
    scaffold = Scaffold(__name__)
    
    # Mock the _check_setup_finished method to avoid NotImplementedError
    def mock_check_setup_finished(f_name):
        pass
    
    monkeypatch.setattr(scaffold, '_check_setup_finished', mock_check_setup_finished)
    
    def first_defaults(endpoint, values):
        values['first'] = 1
    
    def second_defaults(endpoint, values):
        values['second'] = 2
    
    # Register both functions
    scaffold.url_defaults(first_defaults)
    scaffold.url_defaults(second_defaults)
    
    # Verify both functions are registered
    assert first_defaults in scaffold.url_default_functions[None]
    assert second_defaults in scaffold.url_default_functions[None]
    assert len(scaffold.url_default_functions[None]) == 2

def test_url_defaults_empty_initial_state(monkeypatch):
    """Test that url_default_functions starts empty for None key."""
    scaffold = Scaffold(__name__)
    
    # Mock the _check_setup_finished method to avoid NotImplementedError
    def mock_check_setup_finished(f_name):
        pass
    
    monkeypatch.setattr(scaffold, '_check_setup_finished', mock_check_setup_finished)
    
    # Verify initial state is empty list for None key
    assert scaffold.url_default_functions[None] == []
    
    # Register a function and verify it's added
    def test_func(endpoint, values):
        pass
    
    scaffold.url_defaults(test_func)
    assert scaffold.url_default_functions[None] == [test_func]
