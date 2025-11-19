# file: src/flask/src/flask/testing.py:125-133
# asked: {"lines": [125, 126, 127, 128, 129, 130, 131, 132], "branches": []}
# gained: {"lines": [125, 126, 127, 128, 129, 130, 131, 132], "branches": []}

import pytest
from flask import Flask
from flask.testing import FlaskClient


def test_flask_client_init():
    """Test that FlaskClient.__init__ sets up the expected attributes."""
    app = Flask(__name__)
    
    # Create a FlaskClient instance
    client = FlaskClient(app)
    
    # Verify the attributes set in lines 125-132
    assert client.preserve_context is False
    assert client._new_contexts == []
    assert client._context_stack is not None
    assert client.environ_base["REMOTE_ADDR"] == "127.0.0.1"
    assert "Werkzeug/" in client.environ_base["HTTP_USER_AGENT"]
    
    # Verify that the parent class was initialized properly
    assert client.application == app


def test_flask_client_init_with_args():
    """Test FlaskClient.__init__ with additional arguments passed to parent."""
    app = Flask(__name__)
    
    # Create FlaskClient with additional arguments that might be passed to parent
    client = FlaskClient(app, use_cookies=True)
    
    # Verify the attributes set in lines 125-132
    assert client.preserve_context is False
    assert client._new_contexts == []
    assert client._context_stack is not None
    assert client.environ_base["REMOTE_ADDR"] == "127.0.0.1"
    assert "Werkzeug/" in client.environ_base["HTTP_USER_AGENT"]
    
    # Verify that the parent class was initialized properly
    assert client.application == app


def test_flask_client_init_with_kwargs():
    """Test FlaskClient.__init__ with keyword arguments."""
    app = Flask(__name__)
    
    # Create FlaskClient with keyword arguments
    client = FlaskClient(application=app)
    
    # Verify the attributes set in lines 125-132
    assert client.preserve_context is False
    assert client._new_contexts == []
    assert client._context_stack is not None
    assert client.environ_base["REMOTE_ADDR"] == "127.0.0.1"
    assert "Werkzeug/" in client.environ_base["HTTP_USER_AGENT"]
    
    # Verify that the parent class was initialized properly
    assert client.application == app
