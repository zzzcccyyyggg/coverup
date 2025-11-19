# file: src/flask/src/flask/wrappers.py:142-144
# asked: {"lines": [142, 143, 144], "branches": []}
# gained: {"lines": [142, 143, 144], "branches": []}

import pytest
from flask import Flask
from flask.wrappers import Request

def test_request_max_form_parts_setter():
    """Test that the max_form_parts setter properly sets the value."""
    app = Flask(__name__)
    with app.test_request_context():
        request = Request({})
        
        # Test setting to a positive integer
        request.max_form_parts = 1000
        assert request._max_form_parts == 1000
        
        # Test setting to None
        request.max_form_parts = None
        assert request._max_form_parts is None
        
        # Test setting to 0
        request.max_form_parts = 0
        assert request._max_form_parts == 0
