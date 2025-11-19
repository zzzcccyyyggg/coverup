# file: src/flask/src/flask/sessions.py:97-111
# asked: {"lines": [97, 98, 103, 104, 105, 110, 111], "branches": []}
# gained: {"lines": [97, 98, 103, 104, 105, 110, 111], "branches": []}

import pytest
from flask.sessions import NullSession


class TestNullSession:
    """Test cases for NullSession class to achieve full coverage."""
    
    def test_null_session_read_only_access(self):
        """Test that NullSession allows read-only access to empty session."""
        session = NullSession()
        # Should be able to read from empty session without error
        assert len(session) == 0
        assert 'nonexistent_key' not in session
        assert session.get('nonexistent_key') is None
        assert session.get('nonexistent_key', 'default') == 'default'
    
    def test_null_session_setitem_raises_runtime_error(self):
        """Test that __setitem__ raises RuntimeError."""
        session = NullSession()
        with pytest.raises(RuntimeError, match="The session is unavailable because no secret key was set"):
            session['key'] = 'value'
    
    def test_null_session_delitem_raises_runtime_error(self):
        """Test that __delitem__ raises RuntimeError."""
        session = NullSession()
        with pytest.raises(RuntimeError, match="The session is unavailable because no secret key was set"):
            del session['key']
    
    def test_null_session_clear_raises_runtime_error(self):
        """Test that clear raises RuntimeError."""
        session = NullSession()
        with pytest.raises(RuntimeError, match="The session is unavailable because no secret key was set"):
            session.clear()
    
    def test_null_session_pop_raises_runtime_error(self):
        """Test that pop raises RuntimeError."""
        session = NullSession()
        with pytest.raises(RuntimeError, match="The session is unavailable because no secret key was set"):
            session.pop('key')
    
    def test_null_session_popitem_raises_runtime_error(self):
        """Test that popitem raises RuntimeError."""
        session = NullSession()
        with pytest.raises(RuntimeError, match="The session is unavailable because no secret key was set"):
            session.popitem()
    
    def test_null_session_update_raises_runtime_error(self):
        """Test that update raises RuntimeError."""
        session = NullSession()
        with pytest.raises(RuntimeError, match="The session is unavailable because no secret key was set"):
            session.update({'key': 'value'})
    
    def test_null_session_setdefault_raises_runtime_error(self):
        """Test that setdefault raises RuntimeError."""
        session = NullSession()
        with pytest.raises(RuntimeError, match="The session is unavailable because no secret key was set"):
            session.setdefault('key', 'value')
