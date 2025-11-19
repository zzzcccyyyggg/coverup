# file: src/flask/src/flask/wrappers.py:222-257
# asked: {"lines": [222, 223, 240, 242, 244, 246, 247, 253, 254, 257], "branches": [[253, 254], [253, 257]]}
# gained: {"lines": [222, 223, 240, 242, 244, 246, 247, 253, 254, 257], "branches": [[253, 254], [253, 257]]}

import pytest
from flask import Flask
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

class TestResponseMaxCookieSize:
    """Test cases for Response.max_cookie_size property."""
    
    def test_max_cookie_size_with_app_context(self):
        """Test max_cookie_size when current_app is available."""
        app = Flask(__name__)
        app.config["MAX_COOKIE_SIZE"] = 4096
        
        with app.app_context():
            response = Response()
            assert response.max_cookie_size == 4096
    
    def test_max_cookie_size_without_app_context(self):
        """Test max_cookie_size when current_app is None."""
        # Create a response object outside of any app context
        response = Response()
        
        # Get the Werkzeug default value directly
        werkzeug_response = ResponseBase()
        werkzeug_default = werkzeug_response.max_cookie_size
        
        # The Flask response should return the Werkzeug default when no app context
        assert response.max_cookie_size == werkzeug_default
