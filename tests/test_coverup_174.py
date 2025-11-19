# file: src/flask/src/flask/sansio/scaffold.py:641-654
# asked: {"lines": [641, 642, 653, 654], "branches": []}
# gained: {"lines": [641, 642, 653, 654], "branches": []}

import pytest
from flask import Flask
from werkzeug.exceptions import HTTPException, default_exceptions

class TestScaffoldRegisterErrorHandler:
    """Test cases for Scaffold.register_error_handler method."""
    
    def test_register_error_handler_with_http_exception_class(self):
        """Test registering error handler with HTTPException subclass."""
        app = Flask(__name__)
        
        def error_handler(e):
            return "Custom error", 500
        
        # Register handler for HTTPException subclass
        app.register_error_handler(HTTPException, error_handler)
        
        # Verify the handler was registered correctly
        assert HTTPException in app.error_handler_spec[None][None]
        assert app.error_handler_spec[None][None][HTTPException] == error_handler
    
    def test_register_error_handler_with_http_status_code(self):
        """Test registering error handler with HTTP status code."""
        app = Flask(__name__)
        
        def error_handler(e):
            return "Not found", 404
        
        # Register handler for HTTP status code
        app.register_error_handler(404, error_handler)
        
        # Verify the handler was registered correctly
        not_found_exc_class = default_exceptions[404]
        assert not_found_exc_class in app.error_handler_spec[None][404]
        assert app.error_handler_spec[None][404][not_found_exc_class] == error_handler
    
    def test_register_error_handler_with_custom_exception_class(self):
        """Test registering error handler with custom exception class."""
        app = Flask(__name__)
        
        class CustomException(Exception):
            pass
        
        def error_handler(e):
            return "Custom exception", 500
        
        # Register handler for custom exception class
        app.register_error_handler(CustomException, error_handler)
        
        # Verify the handler was registered correctly
        assert CustomException in app.error_handler_spec[None][None]
        assert app.error_handler_spec[None][None][CustomException] == error_handler
