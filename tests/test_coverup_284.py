# file: src/flask/src/flask/cli.py:41-91
# asked: {"lines": [], "branches": [[74, 67]]}
# gained: {"lines": [], "branches": [[74, 67]]}

import pytest
import types
from flask import Flask
from flask.cli import NoAppException, find_best_app, _called_with_wrong_args

def test_find_best_app_factory_create_app_success():
    """Test finding app through create_app factory function that returns Flask instance."""
    module = types.ModuleType("test_module")
    
    def create_app():
        return Flask(__name__)
    
    module.create_app = create_app
    
    app = find_best_app(module)
    assert isinstance(app, Flask)

def test_find_best_app_factory_make_app_success():
    """Test finding app through make_app factory function that returns Flask instance."""
    module = types.ModuleType("test_module")
    
    def make_app():
        return Flask(__name__)
    
    module.make_app = make_app
    
    app = find_best_app(module)
    assert isinstance(app, Flask)

def test_find_best_app_factory_wrong_args():
    """Test factory function that requires arguments and raises TypeError."""
    module = types.ModuleType("test_module")
    
    def create_app(name):
        return Flask(name)
    
    module.create_app = create_app
    
    with pytest.raises(NoAppException) as exc_info:
        find_best_app(module)
    
    assert "could not call it without arguments" in str(exc_info.value)

def test_find_best_app_factory_other_type_error():
    """Test factory function that raises TypeError for reasons other than wrong arguments."""
    module = types.ModuleType("test_module")
    
    def create_app():
        raise TypeError("Some other error")
    
    module.create_app = create_app
    
    with pytest.raises(TypeError) as exc_info:
        find_best_app(module)
    
    assert "Some other error" in str(exc_info.value)

def test_find_best_app_factory_returns_non_flask():
    """Test factory function that returns non-Flask object."""
    module = types.ModuleType("test_module")
    
    def create_app():
        return "not a flask app"
    
    module.create_app = create_app
    
    with pytest.raises(NoAppException) as exc_info:
        find_best_app(module)
    
    assert "Failed to find Flask application or factory" in str(exc_info.value)
