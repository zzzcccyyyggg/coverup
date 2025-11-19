# file: src/flask/src/flask/app.py:1121-1261
# asked: {"lines": [1232, 1233, 1234, 1238, 1239, 1253], "branches": [[1252, 1253]]}
# gained: {"lines": [1232, 1233, 1234, 1238, 1239], "branches": []}

import pytest
from flask import Flask
from werkzeug.wrappers import Response as BaseResponse
from werkzeug.datastructures import Headers
import sys

class TestFlaskMakeResponse:
    """Test cases for Flask.make_response to cover missing lines 1232-1239 and 1253."""
    
    def test_make_response_with_invalid_base_response_force_type(self):
        """Test line 1232-1239: TypeError in force_type with BaseResponse subclass."""
        app = Flask(__name__)
        app.testing = True
        
        with app.test_client() as client:
            # Create a mock BaseResponse subclass that will cause force_type to fail
            class InvalidResponse(BaseResponse):
                pass
            
            # Mock force_type to raise TypeError
            original_force_type = app.response_class.force_type
            
            def mock_force_type(rv, environ):
                raise TypeError("Invalid response type")
            
            app.response_class.force_type = mock_force_type
            
            try:
                # Create an invalid response object
                invalid_response = InvalidResponse()
                
                # This should trigger the TypeError handling in lines 1232-1239
                with pytest.raises(TypeError) as exc_info:
                    with client.application.test_request_context():
                        app.make_response(invalid_response)
                
                assert "Invalid response type" in str(exc_info.value)
                assert "The view function did not return a valid response" in str(exc_info.value)
                assert "InvalidResponse" in str(exc_info.value)
            finally:
                # Restore original force_type
                app.response_class.force_type = original_force_type
    
    def test_make_response_with_string_status(self):
        """Test line 1253: setting status as string/bytes."""
        app = Flask(__name__)
        app.testing = True
        
        with app.test_client() as client:
            with client.application.test_request_context():
                # Test with string status in tuple - this should work
                rv = ("Hello", "200 OK")
                response = app.make_response(rv)
                assert response.status == "200 OK"
                
                # Test with string status after response creation
                response = app.response_class("Hello")
                response.status = "404 NOT FOUND"
                assert response.status == "404 NOT FOUND"
    
    def test_make_response_with_callable_force_type_error(self):
        """Test lines 1232-1239: TypeError in force_type with callable."""
        app = Flask(__name__)
        app.testing = True
        
        with app.test_client() as client:
            # Mock force_type to raise TypeError for callable
            original_force_type = app.response_class.force_type
            
            def mock_force_type(rv, environ):
                raise TypeError("Callable returned invalid response")
            
            app.response_class.force_type = mock_force_type
            
            try:
                # Create a callable that would normally be processed by force_type
                def wsgi_callable(environ, start_response):
                    return [b"test"]
                
                # This should trigger the TypeError handling in lines 1232-1239
                with pytest.raises(TypeError) as exc_info:
                    with client.application.test_request_context():
                        app.make_response(wsgi_callable)
                
                assert "Callable returned invalid response" in str(exc_info.value)
                assert "The view function did not return a valid response" in str(exc_info.value)
                assert "function" in str(exc_info.value)
            finally:
                # Restore original force_type
                app.response_class.force_type = original_force_type
