# file: src/flask/src/flask/sessions.py:189-199
# asked: {"lines": [189, 199], "branches": []}
# gained: {"lines": [189, 199], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface


class TestSessionInterfaceGetCookieDomain:
    """Test cases for SessionInterface.get_cookie_domain method."""
    
    def test_get_cookie_domain_with_value(self):
        """Test get_cookie_domain when SESSION_COOKIE_DOMAIN is set."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_DOMAIN"] = "example.com"
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_domain(app)
        
        assert result == "example.com"
    
    def test_get_cookie_domain_with_none_value(self):
        """Test get_cookie_domain when SESSION_COOKIE_DOMAIN is None."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_DOMAIN"] = None
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_domain(app)
        
        assert result is None
    
    def test_get_cookie_domain_with_empty_string(self):
        """Test get_cookie_domain when SESSION_COOKIE_DOMAIN is empty string."""
        app = Flask(__name__)
        app.config["SESSION_COOKIE_DOMAIN"] = ""
        
        session_interface = SessionInterface()
        result = session_interface.get_cookie_domain(app)
        
        assert result == ""
    
    def test_get_cookie_domain_not_set(self):
        """Test get_cookie_domain when SESSION_COOKIE_DOMAIN is not in config."""
        app = Flask(__name__)
        # Remove SESSION_COOKIE_DOMAIN from config if it exists
        app.config.pop("SESSION_COOKIE_DOMAIN", None)
        
        session_interface = SessionInterface()
        
        # The method should raise KeyError when the config key doesn't exist
        with pytest.raises(KeyError):
            session_interface.get_cookie_domain(app)
