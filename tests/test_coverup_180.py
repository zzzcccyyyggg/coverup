# file: src/flask/src/flask/sansio/app.py:806-821
# asked: {"lines": [806, 807, 808, 821], "branches": []}
# gained: {"lines": [806, 807, 808, 821], "branches": []}

import pytest
from flask import Flask
from flask.typing import TemplateGlobalCallable

def test_add_template_global_with_name():
    """Test add_template_global with explicit name parameter."""
    app = Flask(__name__)
    
    def custom_global():
        return "test_value"
    
    app.add_template_global(custom_global, name="custom_name")
    
    assert "custom_name" in app.jinja_env.globals
    assert app.jinja_env.globals["custom_name"] is custom_global

def test_add_template_global_without_name():
    """Test add_template_global without name parameter (uses function name)."""
    app = Flask(__name__)
    
    def custom_global():
        return "test_value"
    
    app.add_template_global(custom_global)
    
    assert "custom_global" in app.jinja_env.globals
    assert app.jinja_env.globals["custom_global"] is custom_global

def test_add_template_global_with_none_name():
    """Test add_template_global with name=None (uses function name)."""
    app = Flask(__name__)
    
    def custom_global():
        return "test_value"
    
    app.add_template_global(custom_global, name=None)
    
    assert "custom_global" in app.jinja_env.globals
    assert app.jinja_env.globals["custom_global"] is custom_global
