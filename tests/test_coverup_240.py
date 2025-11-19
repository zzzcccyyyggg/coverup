# file: src/flask/src/flask/sessions.py:222-227
# asked: {"lines": [222, 227], "branches": []}
# gained: {"lines": [222, 227], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface

class TestSessionInterface:
    def test_get_cookie_samesite_returns_config_value(self):
        """Test that get_cookie_samesite returns the SESSION_COOKIE_SAMESITE config value."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
        
        interface = SessionInterface()
        result = interface.get_cookie_samesite(app)
        
        assert result == "Strict"

    def test_get_cookie_samesite_returns_none_when_not_set(self):
        """Test that get_cookie_samesite returns None when SESSION_COOKIE_SAMESITE is not set."""
        app = Flask(__name__)
        # Don't set SESSION_COOKIE_SAMESITE
        
        interface = SessionInterface()
        result = interface.get_cookie_samesite(app)
        
        assert result is None

    def test_get_cookie_samesite_returns_lax(self):
        """Test that get_cookie_samesite returns 'Lax' when configured."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        
        interface = SessionInterface()
        result = interface.get_cookie_samesite(app)
        
        assert result == "Lax"
