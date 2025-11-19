# file: src/flask/src/flask/wrappers.py:88-90
# asked: {"lines": [88, 89, 90], "branches": []}
# gained: {"lines": [88, 89, 90], "branches": []}

import pytest
from flask import Flask
from flask.wrappers import Request

def test_request_max_content_length_setter():
    """Test that the max_content_length setter properly sets the value."""
    app = Flask(__name__)
    with app.test_request_context():
        request = Request({})
        
        # Test setting a positive integer
        request.max_content_length = 1024
        assert request._max_content_length == 1024
        
        # Test setting None
        request.max_content_length = None
        assert request._max_content_length is None
        
        # Test setting zero
        request.max_content_length = 0
        assert request._max_content_length == 0
        
        # Test setting a large integer
        request.max_content_length = 1000000
        assert request._max_content_length == 1000000
