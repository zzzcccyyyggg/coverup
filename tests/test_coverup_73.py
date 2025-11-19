# file: src/flask/src/flask/sansio/app.py:716-750
# asked: {"lines": [716, 717, 718, 742, 743, 744, 746, 747, 748, 750], "branches": [[742, 743], [742, 746]]}
# gained: {"lines": [716, 717, 718, 742, 743, 744, 746, 747, 748, 750], "branches": [[742, 743], [742, 746]]}

import pytest
from flask import Flask
from flask.sansio.scaffold import setupmethod
from typing import TypeVar, Callable

T_template_test = TypeVar('T_template_test', bound=Callable)

class TestAppTemplateTest:
    """Test cases for App.template_test method to achieve full coverage."""
    
    def test_template_test_with_callable_name(self):
        """Test template_test when name is a callable (decorator without parentheses)."""
        app = Flask(__name__)
        
        # Define a test function
        def is_even(n):
            return n % 2 == 0
        
        # Register using decorator without parentheses
        result = app.template_test(is_even)
        
        # Verify the function was registered and returned
        assert result is is_even
        assert 'is_even' in app.jinja_env.tests
        assert app.jinja_env.tests['is_even'] is is_even
    
    def test_template_test_with_name_string(self):
        """Test template_test when name is a string (decorator with parentheses)."""
        app = Flask(__name__)
        
        # Define a test function
        def is_odd(n):
            return n % 2 == 1
        
        # Register using decorator with parentheses and custom name
        decorator = app.template_test(name='odd')
        
        # Apply the decorator
        result = decorator(is_odd)
        
        # Verify the function was registered with custom name and returned
        assert result is is_odd
        assert 'odd' in app.jinja_env.tests
        assert app.jinja_env.tests['odd'] is is_odd
    
    def test_template_test_with_none_name(self):
        """Test template_test when name is None (decorator with parentheses but no name)."""
        app = Flask(__name__)
        
        # Define a test function
        def is_positive(n):
            return n > 0
        
        # Register using decorator with parentheses but no name
        decorator = app.template_test(name=None)
        
        # Apply the decorator
        result = decorator(is_positive)
        
        # Verify the function was registered with function name and returned
        assert result is is_positive
        assert 'is_positive' in app.jinja_env.tests
        assert app.jinja_env.tests['is_positive'] is is_positive
