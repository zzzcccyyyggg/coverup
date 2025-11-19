# file: src/flask/src/flask/sessions.py:216-220
# asked: {"lines": [216, 220], "branches": []}
# gained: {"lines": [216, 220], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface

class TestSessionInterface:
    def test_get_cookie_secure_returns_true_when_config_set(self):
        """Test that get_cookie_secure returns True when SESSION_COOKIE_SECURE is True"""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_SECURE"] = True
        session_interface = SessionInterface()
        
        result = session_interface.get_cookie_secure(app)
        
        assert result is True

    def test_get_cookie_secure_returns_false_when_config_set(self):
        """Test that get_cookie_secure returns False when SESSION_COOKIE_SECURE is False"""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_SECURE"] = False
        session_interface = SessionInterface()
        
        result = session_interface.get_cookie_secure(app)
        
        assert result is False

    def test_get_cookie_secure_returns_default_when_config_not_set(self):
        """Test that get_cookie_secure returns default value when SESSION_COOKIE_SECURE is not set"""
        app = Flask(__name__)
        # Ensure SESSION_COOKIE_SECURE is not in config
        if "SESSION_COOKIE_SECURE" in app.config:
            del app.config["SESSION_COOKIE_SECURE"]
        session_interface = SessionInterface()
        
        # This should raise a KeyError since the config key doesn't exist
        with pytest.raises(KeyError):
            session_interface.get_cookie_secure(app)
