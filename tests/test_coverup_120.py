# file: src/flask/src/flask/ctx.py:369-378
# asked: {"lines": [369, 370, 375, 376, 378], "branches": [[375, 376], [375, 378]]}
# gained: {"lines": [369, 370, 375, 376, 378], "branches": [[375, 376], [375, 378]]}

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.wrappers import Request


def test_app_context_request_property_raises_runtime_error_when_no_request():
    """Test that accessing request property raises RuntimeError when _request is None."""
    app = Flask(__name__)
    ctx = AppContext(app)
    
    with pytest.raises(RuntimeError, match="There is no request in this context."):
        _ = ctx.request


def test_app_context_request_property_returns_request_when_set():
    """Test that request property returns the request when _request is set."""
    app = Flask(__name__)
    with app.test_request_context() as ctx:
        # The test_request_context creates an AppContext with request data
        assert ctx.request is not None
        assert isinstance(ctx.request, Request)
