# file: src/flask/src/flask/sessions.py:164-174
# asked: {"lines": [164, 174], "branches": []}
# gained: {"lines": [164, 174], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface, NullSession

class TestSessionInterface:
    def test_make_null_session_returns_null_session_instance(self):
        """Test that make_null_session returns an instance of null_session_class."""
        app = Flask(__name__)
        session_interface = SessionInterface()
        
        result = session_interface.make_null_session(app)
        
        assert isinstance(result, NullSession)
        assert result.__class__ == session_interface.null_session_class

    def test_make_null_session_with_custom_null_session_class(self, monkeypatch):
        """Test that make_null_session uses the custom null_session_class when set."""
        app = Flask(__name__)
        
        class CustomNullSession(NullSession):
            pass
        
        session_interface = SessionInterface()
        monkeypatch.setattr(session_interface, 'null_session_class', CustomNullSession)
        
        result = session_interface.make_null_session(app)
        
        assert isinstance(result, CustomNullSession)
        assert result.__class__ == CustomNullSession
