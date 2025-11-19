# file: src/flask/src/flask/sessions.py:229-235
# asked: {"lines": [229, 235], "branches": []}
# gained: {"lines": [229, 235], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface

class TestSessionInterface:
    def test_get_cookie_partitioned_returns_config_value(self):
        """Test that get_cookie_partitioned returns the SESSION_COOKIE_PARTITIONED config value."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_PARTITIONED"] = True
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_partitioned(app)
        
        assert result is True

    def test_get_cookie_partitioned_returns_false_when_config_false(self):
        """Test that get_cookie_partitioned returns False when SESSION_COOKIE_PARTITIONED is False."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_PARTITIONED"] = False
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_partitioned(app)
        
        assert result is False
