# file: src/flask/src/flask/testing.py:249-253
# asked: {"lines": [249, 250, 251, 252, 253], "branches": [[250, 251], [250, 252]]}
# gained: {"lines": [249, 250, 251, 252, 253], "branches": [[250, 251], [250, 252]]}

import pytest
from flask import Flask
from flask.testing import FlaskClient


def test_flask_client_context_manager_preserve_context_true():
    """Test that entering context manager with preserve_context=True raises RuntimeError."""
    app = Flask(__name__)
    client = app.test_client()
    client.preserve_context = True
    
    with pytest.raises(RuntimeError, match="Cannot nest client invocations"):
        with client:
            pass


def test_flask_client_context_manager_preserve_context_false():
    """Test that entering context manager with preserve_context=False works correctly."""
    app = Flask(__name__)
    client = app.test_client()
    client.preserve_context = False
    
    with client as ctx_client:
        assert ctx_client is client
        assert client.preserve_context is True
