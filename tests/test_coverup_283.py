# file: src/flask/src/flask/sansio/app.py:666-693
# asked: {"lines": [686, 687], "branches": [[685, 686]]}
# gained: {"lines": [686, 687], "branches": [[685, 686]]}

import pytest
from flask import Flask

def test_template_filter_with_callable_name():
    """Test that template_filter works when name is a callable (function)."""
    app = Flask(__name__)
    
    def custom_filter(value):
        return value.upper()
    
    # When name is a callable, it should be registered directly
    result = app.template_filter(custom_filter)
    
    # The function should be returned
    assert result is custom_filter
    
    # The filter should be registered in jinja_env.filters
    assert 'custom_filter' in app.jinja_env.filters
    assert app.jinja_env.filters['custom_filter'] is custom_filter

def test_template_filter_with_name_string():
    """Test that template_filter works when name is a string."""
    app = Flask(__name__)
    
    def custom_filter(value):
        return value.upper()
    
    # When name is a string, it should return a decorator
    decorator = app.template_filter("upper_filter")
    
    # The decorator should register the function
    decorated_func = decorator(custom_filter)
    
    # The original function should be returned
    assert decorated_func is custom_filter
    
    # The filter should be registered with the given name
    assert 'upper_filter' in app.jinja_env.filters
    assert app.jinja_env.filters['upper_filter'] is custom_filter

def test_template_filter_with_none_name():
    """Test that template_filter works when name is None."""
    app = Flask(__name__)
    
    def custom_filter(value):
        return value.upper()
    
    # When name is None, it should return a decorator
    decorator = app.template_filter(None)
    
    # The decorator should register the function with its own name
    decorated_func = decorator(custom_filter)
    
    # The original function should be returned
    assert decorated_func is custom_filter
    
    # The filter should be registered with the function's name
    assert 'custom_filter' in app.jinja_env.filters
    assert app.jinja_env.filters['custom_filter'] is custom_filter
