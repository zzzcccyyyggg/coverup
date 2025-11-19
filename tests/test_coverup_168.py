# file: src/flask/src/flask/sansio/scaffold.py:597-639
# asked: {"lines": [597, 598, 635, 636, 637, 639], "branches": []}
# gained: {"lines": [597, 598, 635, 636, 637, 639], "branches": []}

import pytest
from flask import Flask
from werkzeug.exceptions import HTTPException, NotFound, InternalServerError
import typing as t

T_error_handler = t.TypeVar("T_error_handler", bound=t.Callable[..., t.Any])

class CustomException(Exception):
    pass

class AnotherCustomException(Exception):
    pass

def test_errorhandler_decorator_with_http_status_code():
    """Test errorhandler decorator with HTTP status code."""
    app = Flask(__name__)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return 'Not found', 404
    
    # Verify the handler was registered
    assert 404 in app.error_handler_spec[None]
    assert NotFound in app.error_handler_spec[None][404]
    assert app.error_handler_spec[None][404][NotFound] == handle_not_found

def test_errorhandler_decorator_with_exception_class():
    """Test errorhandler decorator with exception class."""
    app = Flask(__name__)
    
    @app.errorhandler(CustomException)
    def handle_custom_exception(error):
        return 'Custom error', 500
    
    # Verify the handler was registered
    assert None in app.error_handler_spec[None]
    assert CustomException in app.error_handler_spec[None][None]
    assert app.error_handler_spec[None][None][CustomException] == handle_custom_exception

def test_errorhandler_decorator_with_http_exception_class():
    """Test errorhandler decorator with HTTPException subclass."""
    app = Flask(__name__)
    
    @app.errorhandler(InternalServerError)
    def handle_internal_error(error):
        return 'Internal error', 500
    
    # Verify the handler was registered
    assert 500 in app.error_handler_spec[None]
    assert InternalServerError in app.error_handler_spec[None][500]
    assert app.error_handler_spec[None][500][InternalServerError] == handle_internal_error

def test_errorhandler_decorator_returns_original_function():
    """Test that errorhandler decorator returns the original function."""
    app = Flask(__name__)
    
    def handler_function(error):
        return 'Error handled', 500
    
    # Apply decorator and verify it returns the original function
    decorated_function = app.errorhandler(500)(handler_function)
    assert decorated_function == handler_function
    
    # Also verify the handler was registered
    assert 500 in app.error_handler_spec[None]
    assert InternalServerError in app.error_handler_spec[None][500]
    assert app.error_handler_spec[None][500][InternalServerError] == handler_function

def test_errorhandler_decorator_multiple_registrations():
    """Test multiple errorhandler registrations."""
    app = Flask(__name__)
    
    @app.errorhandler(404)
    def handle_404(error):
        return '404 error', 404
    
    @app.errorhandler(500)
    def handle_500(error):
        return '500 error', 500
    
    @app.errorhandler(CustomException)
    def handle_custom(error):
        return 'Custom error', 500
    
    # Verify all handlers were registered correctly
    assert 404 in app.error_handler_spec[None]
    assert 500 in app.error_handler_spec[None]
    assert None in app.error_handler_spec[None]
    
    assert NotFound in app.error_handler_spec[None][404]
    assert InternalServerError in app.error_handler_spec[None][500]
    assert CustomException in app.error_handler_spec[None][None]
    
    assert app.error_handler_spec[None][404][NotFound] == handle_404
    assert app.error_handler_spec[None][500][InternalServerError] == handle_500
    assert app.error_handler_spec[None][None][CustomException] == handle_custom
