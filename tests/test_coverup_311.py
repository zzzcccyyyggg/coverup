# file: src/flask/src/flask/app.py:1121-1261
# asked: {"lines": [1253], "branches": [[1252, 1253]]}
# gained: {"lines": [1253], "branches": [[1252, 1253]]}

import pytest
from flask import Flask
from werkzeug.wrappers import Response as BaseResponse

class TestMakeResponse:
    """Test cases for Flask.make_response method"""
    
    def test_make_response_with_string_status(self):
        """Test that line 1253 executes when status is a string"""
        app = Flask(__name__)
        
        # Create a response with string status
        with app.test_request_context():
            response = app.make_response(("body", "200 OK"))
            
            # Verify the response has the correct status
            assert response.status == "200 OK"
            assert response.data == b"body"
    
    def test_make_response_with_string_status_on_existing_response(self):
        """Test that line 1253 executes when status is string on existing response"""
        app = Flask(__name__)
        
        # Create a response object and then pass it with string status
        with app.test_request_context():
            original_response = app.response_class("body")
            response = app.make_response((original_response, "302 Found"))
            
            # Verify the response has the correct status
            assert response.status == "302 Found"
            assert response.data == b"body"
    
    def test_make_response_with_string_status_and_headers(self):
        """Test that line 1253 executes with string status and headers"""
        app = Flask(__name__)
        
        # Create a response with string status and headers
        with app.test_request_context():
            response = app.make_response(("body", "201 Created", {"X-Custom": "value"}))
            
            # Verify the response has the correct status and headers
            assert response.status == "201 Created"
            assert response.data == b"body"
            assert response.headers["X-Custom"] == "value"
