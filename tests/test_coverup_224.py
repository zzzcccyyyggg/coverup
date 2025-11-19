# file: src/flask/src/flask/sessions.py:247-261
# asked: {"lines": [247, 259, 260], "branches": []}
# gained: {"lines": [247, 259, 260], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface, SessionMixin

class MockSession(SessionMixin):
    def __init__(self, modified=False, permanent=False):
        self._modified = modified
        self._permanent = permanent
        self._data = {}
    
    @property
    def modified(self):
        return self._modified
    
    @modified.setter
    def modified(self, value):
        self._modified = value
    
    @property
    def permanent(self):
        return self._permanent
    
    @permanent.setter
    def permanent(self, value):
        self._permanent = value
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
        self._modified = True
    
    def __delitem__(self, key):
        del self._data[key]
        self._modified = True
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)

class TestSessionInterfaceShouldSetCookie:
    def test_should_set_cookie_when_session_modified(self):
        """Test that cookie should be set when session is modified."""
        app = Flask(__name__)
        session = MockSession(modified=True, permanent=False)
        interface = SessionInterface()
        
        result = interface.should_set_cookie(app, session)
        
        assert result is True

    def test_should_set_cookie_when_permanent_and_refresh_enabled(self):
        """Test that cookie should be set when session is permanent and refresh is enabled."""
        app = Flask(__name__)
        app.config["SESSION_REFRESH_EACH_REQUEST"] = True
        session = MockSession(modified=False, permanent=True)
        interface = SessionInterface()
        
        result = interface.should_set_cookie(app, session)
        
        assert result is True

    def test_should_not_set_cookie_when_not_modified_and_not_permanent(self):
        """Test that cookie should not be set when session is not modified and not permanent."""
        app = Flask(__name__)
        app.config["SESSION_REFRESH_EACH_REQUEST"] = True
        session = MockSession(modified=False, permanent=False)
        interface = SessionInterface()
        
        result = interface.should_set_cookie(app, session)
        
        assert result is False

    def test_should_not_set_cookie_when_permanent_and_refresh_disabled(self):
        """Test that cookie should not be set when session is permanent but refresh is disabled."""
        app = Flask(__name__)
        app.config["SESSION_REFRESH_EACH_REQUEST"] = False
        session = MockSession(modified=False, permanent=True)
        interface = SessionInterface()
        
        result = interface.should_set_cookie(app, session)
        
        assert result is False

    def test_should_set_cookie_when_modified_and_permanent_with_refresh_disabled(self):
        """Test that cookie should be set when session is modified, even if permanent with refresh disabled."""
        app = Flask(__name__)
        app.config["SESSION_REFRESH_EACH_REQUEST"] = False
        session = MockSession(modified=True, permanent=True)
        interface = SessionInterface()
        
        result = interface.should_set_cookie(app, session)
        
        assert result is True
