# file: src/flask/src/flask/sansio/app.py:865-888
# asked: {"lines": [], "branches": [[883, 877], [886, 883]]}
# gained: {"lines": [], "branches": [[883, 877], [886, 883]]}

import pytest
from flask import Flask
from werkzeug.exceptions import HTTPException

class CustomException(Exception):
    pass

class CustomHTTPException(HTTPException):
    code = 418

def test_find_error_handler_empty_handler_map():
    """Test when handler_map exists but is empty, should continue to next iteration"""
    app = Flask(__name__)
    
    # Register an error handler for a specific code but with empty handler_map
    # This will trigger the continue statement at line 883
    app.error_handler_spec[None][418] = {}  # Empty handler map
    
    # Create an exception that would match the code
    exc = CustomHTTPException()
    
    # This should return None since handler_map is empty
    result = app._find_error_handler(exc, [])
    assert result is None

def test_find_error_handler_no_matching_class_in_mro():
    """Test when handler_map has entries but no matching class in MRO"""
    app = Flask(__name__)
    
    # Register a handler for a class that's not in the exception's MRO
    def dummy_handler(e):
        return "handler"
    
    # Register handler for a class that won't be in CustomException's MRO
    class UnrelatedException(Exception):
        pass
    
    app.error_handler_spec[None][None] = {UnrelatedException: dummy_handler}
    
    # Create CustomException which has different MRO than UnrelatedException
    exc = CustomException()
    
    # This should iterate through all classes in MRO without finding a match
    # and return None, executing the full MRO loop without early return
    result = app._find_error_handler(exc, [])
    assert result is None

def test_find_error_handler_blueprint_empty_handler_map():
    """Test blueprint scenario with empty handler map"""
    app = Flask(__name__)
    
    # Set up blueprint error handler spec with empty map
    app.error_handler_spec['test_blueprint'] = {None: {}}
    
    exc = CustomException()
    
    # This should check the blueprint first, find empty handler map, continue to app
    result = app._find_error_handler(exc, ['test_blueprint'])
    assert result is None

def test_find_error_handler_code_with_empty_handler_map():
    """Test when code is not None but handler map is empty"""
    app = Flask(__name__)
    
    # Set up handler spec for specific code with empty map
    app.error_handler_spec[None][418] = {}
    
    exc = CustomHTTPException()
    
    # This should iterate through code then None, both with empty maps
    result = app._find_error_handler(exc, [])
    assert result is None
