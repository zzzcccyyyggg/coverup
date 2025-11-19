# file: src/flask/src/flask/sansio/app.py:935-951
# asked: {"lines": [935, 947, 948, 949, 950], "branches": []}
# gained: {"lines": [935, 947, 948, 949, 950], "branches": []}

import pytest
from flask import Flask
from werkzeug.wrappers import Response as BaseResponse


class TestAppRedirect:
    """Test cases for the App.redirect method."""
    
    def test_redirect_default_code(self):
        """Test redirect with default status code (302)."""
        app = Flask(__name__)
        response = app.redirect('http://example.com')
        
        assert isinstance(response, BaseResponse)
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://example.com'
    
    def test_redirect_custom_code(self):
        """Test redirect with custom status code."""
        app = Flask(__name__)
        response = app.redirect('http://example.com', code=301)
        
        assert isinstance(response, BaseResponse)
        assert response.status_code == 301
        assert response.headers['Location'] == 'http://example.com'
    
    def test_redirect_with_response_class(self):
        """Test that redirect uses the app's response_class."""
        app = Flask(__name__)
        
        # Verify the response_class is used by checking the response type
        response = app.redirect('http://example.com')
        assert isinstance(response, app.response_class)
