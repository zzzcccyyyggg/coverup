# file: src/flask/src/flask/sansio/app.py:662-665
# asked: {"lines": [662, 663, 664, 665], "branches": []}
# gained: {"lines": [662, 663, 664], "branches": []}

import pytest
import typing as t
from flask import Flask

def test_template_filter_overload_with_name_none():
    """Test the template_filter overload when name is None."""
    app = Flask(__name__)
    
    # This should call the overload that returns a decorator function
    decorator = app.template_filter(name=None)
    
    # Verify it returns a callable that can be used as a decorator
    assert callable(decorator)
    
    # Test that the decorator works correctly
    @decorator
    def test_filter(value):
        return value.upper()
    
    # Verify the filter was registered
    assert 'test_filter' in app.jinja_env.filters
    assert app.jinja_env.filters['test_filter'] is test_filter

def test_template_filter_overload_with_name_none_cleanup():
    """Test the template_filter overload when name is None with cleanup."""
    app = Flask(__name__)
    
    # Get the decorator function
    decorator = app.template_filter(name=None)
    
    # Use the decorator to register a filter
    @decorator
    def custom_filter(value):
        return f"filtered_{value}"
    
    # Verify the filter was registered
    assert 'custom_filter' in app.jinja_env.filters
    
    # Clean up by removing the filter
    del app.jinja_env.filters['custom_filter']
    assert 'custom_filter' not in app.jinja_env.filters

def test_template_filter_overload_with_name_none_multiple_filters():
    """Test the template_filter overload when name is None with multiple filters."""
    app = Flask(__name__)
    
    # Get the decorator function
    decorator = app.template_filter(name=None)
    
    # Register multiple filters using the same decorator
    @decorator
    def filter1(value):
        return value + "_1"
    
    @decorator  
    def filter2(value):
        return value + "_2"
    
    # Verify both filters were registered with their function names
    assert 'filter1' in app.jinja_env.filters
    assert 'filter2' in app.jinja_env.filters
    assert app.jinja_env.filters['filter1'] is filter1
    assert app.jinja_env.filters['filter2'] is filter2
    
    # Clean up
    del app.jinja_env.filters['filter1']
    del app.jinja_env.filters['filter2']
