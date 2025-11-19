# file: src/flask/src/flask/cli.py:120-197
# asked: {"lines": [152, 154, 192], "branches": [[191, 192]]}
# gained: {"lines": [152, 154, 192], "branches": [[191, 192]]}

import pytest
import ast
import inspect
from types import ModuleType
from flask.app import Flask
from flask.cli import find_app_by_string, NoAppException

def test_find_app_by_string_with_keyword_arguments():
    """Test line 152: keyword arguments processing with non-None arg names"""
    # Create a test module with a factory function
    test_module = ModuleType('test_module')
    
    def create_app(host='localhost', port=5000):
        return Flask(__name__)
    
    test_module.create_app = create_app
    
    # Test with keyword arguments that have non-None arg names
    app_name = "create_app(host='127.0.0.1', port=8080)"
    app = find_app_by_string(test_module, app_name)
    
    assert isinstance(app, Flask)

def test_find_app_by_string_with_none_keyword_arg():
    """Test line 154: keyword arguments processing with None arg (should be skipped)"""
    # Create a test module with a factory function
    test_module = ModuleType('test_module')
    
    def create_app(**kwargs):
        return Flask(__name__)
    
    test_module.create_app = create_app
    
    # This should trigger the line 154 condition where kw.arg is None
    # We need to create an AST with a keyword argument that has None as arg
    # This happens with **kwargs expansion in Python 3.5+
    app_name = "create_app(**{'debug': True})"
    
    # The function should handle this and skip the None arg
    app = find_app_by_string(test_module, app_name)
    
    assert isinstance(app, Flask)

def test_find_app_by_string_return_app_instance_check():
    """Test line 192: the isinstance check for Flask instance"""
    # Create a test module with a Flask instance
    test_module = ModuleType('test_module')
    flask_app = Flask(__name__)
    test_module.app = flask_app
    
    # This should trigger the isinstance check at line 191-192
    app_name = "app"
    result = find_app_by_string(test_module, app_name)
    
    assert result is flask_app
    assert isinstance(result, Flask)

def test_find_app_by_string_with_invalid_app_type():
    """Test the branch after line 192 when app is not a Flask instance"""
    # Create a test module with a non-Flask object
    test_module = ModuleType('test_module')
    test_module.not_an_app = "not a flask app"
    
    # This should raise NoAppException because the object is not a Flask instance
    app_name = "not_an_app"
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(test_module, app_name)
    
    assert "A valid Flask application was not obtained" in str(exc_info.value)
