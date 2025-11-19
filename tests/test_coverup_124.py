# file: src/flask/src/flask/app.py:664-720
# asked: {"lines": [664, 715, 716, 717, 718, 719], "branches": [[716, 717], [716, 718]]}
# gained: {"lines": [664, 715, 716, 717, 718, 719], "branches": [[716, 717], [716, 718]]}

import pytest
from flask import Flask
from flask.testing import FlaskClient

class CustomTestClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self.custom_arg = kwargs.pop('custom_arg', None)
        super().__init__(*args, **kwargs)

def test_test_client_default():
    """Test test_client with default parameters."""
    app = Flask(__name__)
    client = app.test_client()
    assert isinstance(client, FlaskClient)
    assert client.application is app

def test_test_client_with_custom_class():
    """Test test_client with custom test_client_class."""
    app = Flask(__name__)
    app.test_client_class = CustomTestClient
    client = app.test_client()
    assert isinstance(client, CustomTestClient)
    assert client.application is app

def test_test_client_with_kwargs():
    """Test test_client with additional keyword arguments."""
    app = Flask(__name__)
    app.test_client_class = CustomTestClient
    client = app.test_client(custom_arg='test_value')
    assert isinstance(client, CustomTestClient)
    assert client.custom_arg == 'test_value'

def test_test_client_use_cookies_false():
    """Test test_client with use_cookies=False."""
    app = Flask(__name__)
    client = app.test_client(use_cookies=False)
    assert isinstance(client, FlaskClient)
    assert client.application is app

def test_test_client_context_manager():
    """Test test_client used as context manager."""
    app = Flask(__name__)
    with app.test_client() as client:
        assert isinstance(client, FlaskClient)
        assert client.application is app

def test_test_client_with_none_class():
    """Test test_client when test_client_class is None (default case)."""
    app = Flask(__name__)
    app.test_client_class = None
    client = app.test_client()
    assert isinstance(client, FlaskClient)
    assert client.application is app
