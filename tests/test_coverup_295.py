# file: src/flask/src/flask/testing.py:135-183
# asked: {"lines": [174], "branches": [[173, 174]]}
# gained: {"lines": [174], "branches": [[173, 174]]}

import pytest
from flask import Flask
from flask.sessions import SessionInterface, SessionMixin
from collections.abc import MutableMapping
from typing import Any


class NullSession(SessionMixin, MutableMapping):
    """A concrete null session implementation."""
    
    def __init__(self):
        self._data = {}
    
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
    """A test session interface that can be configured to return null sessions."""
    
    def __init__(self, return_null_session=False):
        super().__init__()
        self.return_null_session = return_null_session
        self.null_session_class = NullSession
    
    def open_session(self, app, request):
        if self.return_null_session:
            return NullSession()
        return {'_permanent': True}  # Return a regular session dict
    
    def save_session(self, app, session, response):
        pass  # No-op for testing
    
    def is_null_session(self, obj):
        return isinstance(obj, self.null_session_class)


def test_session_transaction_with_null_session():
    """Test that session_transaction returns early when session is null."""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    # Configure session interface to return null sessions
    session_interface = TestSessionInterface(return_null_session=True)
    app.session_interface = session_interface
    
    # Create client with cookies enabled
    client = app.test_client(use_cookies=True)
    
    # Track if save_session was called
    save_called = False
    
    def mock_save_session(app, session, response):
        nonlocal save_called
        save_called = True
    
    session_interface.save_session = mock_save_session
    
    # This should execute line 174 (return early for null session)
    with client.session_transaction() as session:
        # Verify we got a null session
        assert isinstance(session, NullSession)
        # The session should be identified as null
        assert app.session_interface.is_null_session(session)
    
    # Verify save_session was NOT called for null session
    assert not save_called


def test_session_transaction_with_regular_session():
    """Test that session_transaction saves regular sessions properly."""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    # Configure session interface to return regular sessions
    session_interface = TestSessionInterface(return_null_session=False)
    app.session_interface = session_interface
    
    # Create client with cookies enabled
    client = app.test_client(use_cookies=True)
    
    # Track if save_session was called
    save_called = False
    
    def mock_save_session(app, session, response):
        nonlocal save_called
        save_called = True
    
    session_interface.save_session = mock_save_session
    
    # This should NOT execute line 174 (regular session should be saved)
    with client.session_transaction() as session:
        # Verify we got a regular session
        assert isinstance(session, dict)
        # The session should NOT be identified as null
        assert not app.session_interface.is_null_session(session)
        # Modify the session
        session['test_key'] = 'test_value'
    
    # Verify save_session was called for regular session
    assert save_called
