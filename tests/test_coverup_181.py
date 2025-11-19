# file: src/flask/src/flask/ctx.py:349-352
# asked: {"lines": [349, 350, 352], "branches": []}
# gained: {"lines": [349, 350, 352], "branches": []}

import pytest
from flask import Flask
from flask.ctx import AppContext

class TestAppContextHasRequest:
    """Test cases for AppContext.has_request property."""
    
    def test_has_request_with_request(self):
        """Test has_request returns True when _request is not None."""
        app = Flask(__name__)
        request = app.test_request_context().request
        
        # Create AppContext with a request
        ctx = AppContext(app, request=request)
        
        # Verify has_request returns True when _request is set
        assert ctx.has_request is True
    
    def test_has_request_without_request(self):
        """Test has_request returns False when _request is None."""
        app = Flask(__name__)
        
        # Create AppContext without a request
        ctx = AppContext(app)
        
        # Verify has_request returns False when _request is None
        assert ctx.has_request is False
