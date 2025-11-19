# file: src/flask/src/flask/sansio/app.py:752-767
# asked: {"lines": [752, 753, 754, 767], "branches": []}
# gained: {"lines": [752, 753, 754, 767], "branches": []}

import pytest
from flask import Flask
from flask.sansio.scaffold import Scaffold

def test_add_template_test_with_name():
    """Test add_template_test with explicit name parameter."""
    app = Flask(__name__)
    
    def custom_test(value):
        return isinstance(value, str)
    
    app.add_template_test(custom_test, name="is_string")
    
    assert "is_string" in app.jinja_env.tests
    assert app.jinja_env.tests["is_string"] is custom_test

def test_add_template_test_without_name():
    """Test add_template_test without name parameter (uses function name)."""
    app = Flask(__name__)
    
    def custom_test(value):
        return isinstance(value, int)
    
    app.add_template_test(custom_test)
    
    assert "custom_test" in app.jinja_env.tests
    assert app.jinja_env.tests["custom_test"] is custom_test

def test_add_template_test_decorator_usage():
    """Test add_template_test used via the template_test decorator pattern."""
    app = Flask(__name__)
    
    @app.template_test()
    def is_even(value):
        return value % 2 == 0
    
    assert "is_even" in app.jinja_env.tests
    assert app.jinja_env.tests["is_even"] is is_even

def test_add_template_test_decorator_with_name():
    """Test add_template_test decorator with explicit name."""
    app = Flask(__name__)
    
    @app.template_test(name="divisible_by_three")
    def divisible_by_three(value):
        return value % 3 == 0
    
    assert "divisible_by_three" in app.jinja_env.tests
    assert app.jinja_env.tests["divisible_by_three"] is divisible_by_three
