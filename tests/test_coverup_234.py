# file: src/flask/src/flask/sessions.py:209-214
# asked: {"lines": [209, 214], "branches": []}
# gained: {"lines": [209, 214], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface

class TestSessionInterface:
    def test_get_cookie_httponly_returns_config_value(self):
        """Test that get_cookie_httponly returns the SESSION_COOKIE_HTTPONLY config value."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_httponly(app)
        
        assert result is True

    def test_get_cookie_httponly_returns_false_when_config_false(self):
        """Test that get_cookie_httponly returns False when SESSION_COOKIE_HTTPONLY is False."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_HTTPONLY"] = False
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_httponly(app)
        
        assert result is False
