# file: src/flask/src/flask/sessions.py:176-183
# asked: {"lines": [176, 183], "branches": []}
# gained: {"lines": [176, 183], "branches": []}

import pytest
from flask.sessions import SessionInterface, NullSession

class TestSessionInterface:
    def test_is_null_session_with_null_session(self):
        """Test that is_null_session returns True for NullSession instances"""
        session_interface = SessionInterface()
        null_session = NullSession()
        
        result = session_interface.is_null_session(null_session)
        
        assert result is True

    def test_is_null_session_with_non_null_session(self):
        """Test that is_null_session returns False for non-NullSession instances"""
        session_interface = SessionInterface()
        regular_dict = {}
        
        result = session_interface.is_null_session(regular_dict)
        
        assert result is False

    def test_is_null_session_with_none(self):
        """Test that is_null_session returns False for None"""
        session_interface = SessionInterface()
        
        result = session_interface.is_null_session(None)
        
        assert result is False

    def test_is_null_session_with_custom_null_session_class(self, monkeypatch):
        """Test that is_null_session works with custom null_session_class"""
        class CustomNullSession:
            pass
        
        session_interface = SessionInterface()
        monkeypatch.setattr(session_interface, 'null_session_class', CustomNullSession)
        custom_null_session = CustomNullSession()
        
        result = session_interface.is_null_session(custom_null_session)
        
        assert result is True
