# file: src/flask/src/flask/sessions.py:185-187
# asked: {"lines": [185, 187], "branches": []}
# gained: {"lines": [185, 187], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface

class TestSessionInterface:
    def test_get_cookie_name_returns_config_value(self):
        """Test that get_cookie_name returns the SESSION_COOKIE_NAME from app config."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_NAME"] = "custom_session"
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_name(app)
        
        assert result == "custom_session"
