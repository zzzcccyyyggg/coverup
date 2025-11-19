# file: src/flask/src/flask/ctx.py:208-231
# asked: {"lines": [208, 231], "branches": []}
# gained: {"lines": [208, 231], "branches": []}

import pytest
from flask import Flask, has_request_context
from flask.globals import _cv_app

class TestHasRequestContext:
    def test_has_request_context_without_app_context(self):
        """Test has_request_context returns False when no app context is active."""
        # Ensure no app context is active
        while _cv_app.get(None) is not None:
            _cv_app.get(None).pop()
        
        result = has_request_context()
        assert result is False

    def test_has_request_context_with_app_context_no_request(self, app):
        """Test has_request_context returns False when app context is active but no request context."""
        with app.app_context():
            result = has_request_context()
            assert result is False

    def test_has_request_context_with_request_context(self, app):
        """Test has_request_context returns True when request context is active."""
        with app.test_request_context():
            result = has_request_context()
            assert result is True

    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        return app
