# file: src/flask/src/flask/sessions.py:237-245
# asked: {"lines": [237, 243, 244, 245], "branches": [[243, 244], [243, 245]]}
# gained: {"lines": [237, 243, 244, 245], "branches": [[243, 244], [243, 245]]}

import pytest
from datetime import datetime, timedelta, timezone
from flask.app import Flask
from flask.sessions import SessionInterface, SessionMixin
from unittest.mock import Mock

class TestSession(SessionMixin):
    def __init__(self, permanent=False):
        self._permanent = permanent
        self._data = {}
    
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
    
    def __delitem__(self, key):
        del self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)

class TestSessionInterface(SessionInterface):
    pass

class TestGetExpirationTime:
    def test_get_expiration_time_with_permanent_session(self):
        """Test that get_expiration_time returns correct datetime for permanent session."""
        app = Flask(__name__)
        app.permanent_session_lifetime = timedelta(days=1)
        
        session = TestSession(permanent=True)
        interface = TestSessionInterface()
        
        result = interface.get_expiration_time(app, session)
        
        assert result is not None
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
        
        # Check that the expiration time is approximately now + 1 day
        expected_min = datetime.now(timezone.utc) + timedelta(days=1) - timedelta(seconds=1)
        expected_max = datetime.now(timezone.utc) + timedelta(days=1) + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_get_expiration_time_with_non_permanent_session(self):
        """Test that get_expiration_time returns None for non-permanent session."""
        app = Flask(__name__)
        app.permanent_session_lifetime = timedelta(days=1)
        
        session = TestSession(permanent=False)
        interface = TestSessionInterface()
        
        result = interface.get_expiration_time(app, session)
        
        assert result is None
