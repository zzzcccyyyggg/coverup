# file: src/flask/src/flask/app.py:949-960
# asked: {"lines": [949, 956, 957, 958, 959, 960], "branches": []}
# gained: {"lines": [949, 956, 957, 958, 959, 960], "branches": []}

import pytest
from flask import Flask
from flask.wrappers import Response
from flask.globals import _cv_app

class TestFlaskMakeDefaultOptionsResponse:
    """Test cases for Flask.make_default_options_response method."""
    
    def test_make_default_options_response_with_request_context(self):
        """Test that make_default_options_response works correctly within a request context."""
        app = Flask(__name__)
        
        # Add a route to ensure the URL adapter has methods
        @app.route('/test', methods=['GET', 'POST', 'OPTIONS'])
        def test_route():
            return "test"
        
        with app.test_request_context('/test'):
            response = app.make_default_options_response()
            
            # Verify the response is of the correct type
            assert isinstance(response, Response)
            
            # Verify the response has allow header set with methods
            adapter = _cv_app.get().url_adapter
            expected_methods = adapter.allowed_methods()
            assert response.allow == set(expected_methods)
    
    def test_make_default_options_response_creates_empty_response(self):
        """Test that make_default_options_response creates a new response object."""
        app = Flask(__name__)
        
        # Add a route to ensure the URL adapter has methods
        @app.route('/test', methods=['GET', 'POST', 'OPTIONS'])
        def test_route():
            return "test"
        
        with app.test_request_context('/test'):
            response = app.make_default_options_response()
            
            # Verify it's a new response instance
            assert response is not None
            assert isinstance(response, Response)
            
            # Verify the response is empty (no body set)
            assert response.get_data() == b''
