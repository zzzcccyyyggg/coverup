# file: src/flask/src/flask/helpers.py:138-184
# asked: {"lines": [138, 180, 181, 182, 183, 184], "branches": [[180, 181], [180, 182], [182, 183], [182, 184]]}
# gained: {"lines": [138, 180, 181, 182, 183, 184], "branches": [[180, 181], [180, 182], [182, 183], [182, 184]]}

import pytest
from flask import Flask, Response
from flask.helpers import make_response


class TestMakeResponse:
    """Test cases for flask.helpers.make_response function."""

    def test_make_response_no_args(self):
        """Test make_response with no arguments."""
        app = Flask(__name__)
        with app.app_context():
            response = make_response()
            assert isinstance(response, Response)
            assert response.status_code == 200
            assert response.data == b""

    def test_make_response_single_arg_string(self):
        """Test make_response with a single string argument."""
        app = Flask(__name__)
        with app.app_context():
            response = make_response("Hello, World!")
            assert isinstance(response, Response)
            assert response.status_code == 200
            assert response.data == b"Hello, World!"

    def test_make_response_single_arg_response_object(self):
        """Test make_response with a single Response object argument."""
        app = Flask(__name__)
        with app.app_context():
            original_response = Response("Original", status=201)
            response = make_response(original_response)
            assert response is original_response
            assert response.status_code == 201
            assert response.data == b"Original"

    def test_make_response_multiple_args(self):
        """Test make_response with multiple arguments."""
        app = Flask(__name__)
        with app.app_context():
            response = make_response("Test Body", 404, {"X-Custom": "Header"})
            assert isinstance(response, Response)
            assert response.status_code == 404
            assert response.data == b"Test Body"
            assert response.headers["X-Custom"] == "Header"

    def test_make_response_multiple_args_with_list(self):
        """Test make_response with multiple arguments including a list."""
        app = Flask(__name__)
        with app.app_context():
            response = make_response(["item1", "item2"], 201)
            assert isinstance(response, Response)
            assert response.status_code == 201
            assert response.json == ["item1", "item2"]

    def test_make_response_multiple_args_with_dict(self):
        """Test make_response with multiple arguments including a dict."""
        app = Flask(__name__)
        with app.app_context():
            response = make_response({"key": "value"}, 200, [("X-Header", "Value")])
            assert isinstance(response, Response)
            assert response.status_code == 200
            assert response.json == {"key": "value"}
            assert response.headers["X-Header"] == "Value"
