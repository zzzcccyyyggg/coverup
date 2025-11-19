# file: src/flask/src/flask/sansio/app.py:695-708
# asked: {"lines": [695, 696, 697, 708], "branches": []}
# gained: {"lines": [695, 696, 697, 708], "branches": []}

import pytest
from flask import Flask
from flask.sansio.app import App

class TestAppAddTemplateFilter:
    """Test cases for App.add_template_filter method."""
    
    def test_add_template_filter_with_name(self):
        """Test adding a template filter with explicit name."""
        app = Flask(__name__)
        
        def custom_filter(value):
            return value.upper()
        
        app.add_template_filter(custom_filter, name='uppercase')
        
        assert 'uppercase' in app.jinja_env.filters
        assert app.jinja_env.filters['uppercase'] is custom_filter
    
    def test_add_template_filter_without_name(self):
        """Test adding a template filter without explicit name (uses function name)."""
        app = Flask(__name__)
        
        def custom_filter(value):
            return value.lower()
        
        app.add_template_filter(custom_filter)
        
        assert 'custom_filter' in app.jinja_env.filters
        assert app.jinja_env.filters['custom_filter'] is custom_filter
    
    def test_add_template_filter_overwrite_existing(self):
        """Test that adding a template filter overwrites existing filter with same name."""
        app = Flask(__name__)
        
        def first_filter(value):
            return value + "_first"
        
        def second_filter(value):
            return value + "_second"
        
        # Add first filter
        app.add_template_filter(first_filter, name='test_filter')
        assert app.jinja_env.filters['test_filter'] is first_filter
        
        # Add second filter with same name - should overwrite
        app.add_template_filter(second_filter, name='test_filter')
        assert app.jinja_env.filters['test_filter'] is second_filter
    
    def test_add_template_filter_lambda_function(self):
        """Test adding a lambda function as template filter."""
        app = Flask(__name__)
        
        app.add_template_filter(lambda x: x * 2, name='double')
        
        assert 'double' in app.jinja_env.filters
        assert app.jinja_env.filters['double'](5) == 10
    
    def test_add_template_filter_with_none_name(self):
        """Test adding a template filter with None name (should use function name)."""
        app = Flask(__name__)
        
        def my_filter(value):
            return value[::-1]
        
        app.add_template_filter(my_filter, name=None)
        
        assert 'my_filter' in app.jinja_env.filters
        assert app.jinja_env.filters['my_filter'] is my_filter
