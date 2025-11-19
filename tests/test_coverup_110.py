# file: src/flask/src/flask/ctx.py:494-501
# asked: {"lines": [494, 495, 496, 497, 498, 501], "branches": [[495, 496], [495, 501]]}
# gained: {"lines": [494, 495, 496, 497, 498, 501], "branches": [[495, 496], [495, 501]]}

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.wrappers import Request

class TestAppContextRepr:
    def test_repr_with_request(self):
        """Test AppContext.__repr__ when _request is not None"""
        app = Flask(__name__)
        # Create a request with specific URL components
        request = Request.from_values(
            method='GET',
            path='/test',
            base_url='http://localhost:5000'
        )
        ctx = AppContext(app, request=request)
        
        result = repr(ctx)
        assert f"<AppContext {id(ctx)} of {app.name}," in result
        assert "GET" in result
        assert "'http://localhost:5000/test'" in result

    def test_repr_without_request(self):
        """Test AppContext.__repr__ when _request is None"""
        app = Flask(__name__)
        ctx = AppContext(app)
        
        result = repr(ctx)
        assert f"<AppContext {id(ctx)} of {app.name}>" == result
