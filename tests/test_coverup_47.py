# file: src/flask/src/flask/sessions.py:52-94
# asked: {"lines": [52, 53, 66, 72, 74, 76, 78, 79, 80, 82, 84, 85, 86, 88, 89, 90, 92, 93, 94], "branches": []}
# gained: {"lines": [52, 53, 66, 72, 74, 76, 78, 79, 80, 82, 84, 85, 86, 88, 89, 90, 92, 93, 94], "branches": []}

import pytest
from flask.sessions import SecureCookieSession


class TestSecureCookieSession:
    def test_init_with_initial_data(self):
        """Test initialization with initial data."""
        initial_data = {"key1": "value1", "key2": "value2"}
        session = SecureCookieSession(initial_data)
        
        # The session should be accessed during initialization when data is populated
        assert session["key1"] == "value1"
        assert session["key2"] == "value2"
        assert session.modified is False
        assert session.accessed is True  # Initialization accesses the session

    def test_init_with_none(self):
        """Test initialization with None."""
        session = SecureCookieSession(None)
        
        assert len(session) == 0
        assert session.modified is False
        assert session.accessed is False  # No data to access with None

    def test_init_with_iterable(self):
        """Test initialization with iterable of tuples."""
        initial_data = [("key1", "value1"), ("key2", "value2")]
        session = SecureCookieSession(initial_data)
        
        # The session should be accessed during initialization when data is populated
        assert session["key1"] == "value1"
        assert session["key2"] == "value2"
        assert session.modified is False
        assert session.accessed is True  # Initialization accesses the session

    def test_getitem_sets_accessed(self):
        """Test that __getitem__ sets accessed flag."""
        session = SecureCookieSession({"key": "value"})
        
        # Reset accessed flag after initialization
        session.accessed = False
        
        # Access via __getitem__
        value = session["key"]
        
        assert value == "value"
        assert session.accessed is True
        assert session.modified is False

    def test_get_sets_accessed(self):
        """Test that get method sets accessed flag."""
        session = SecureCookieSession({"key": "value"})
        
        # Reset accessed flag after initialization
        session.accessed = False
        
        # Access via get
        value = session.get("key")
        
        assert value == "value"
        assert session.accessed is True
        assert session.modified is False

    def test_get_with_default_sets_accessed(self):
        """Test that get with default value sets accessed flag."""
        session = SecureCookieSession()
        
        # Initially not accessed (empty session)
        assert session.accessed is False
        
        # Access via get with default
        value = session.get("nonexistent", "default_value")
        
        assert value == "default_value"
        assert session.accessed is True
        assert session.modified is False

    def test_setdefault_sets_accessed(self):
        """Test that setdefault method sets accessed flag."""
        session = SecureCookieSession()
        
        # Initially not accessed (empty session)
        assert session.accessed is False
        
        # Access via setdefault
        value = session.setdefault("key", "default_value")
        
        assert value == "default_value"
        assert session.accessed is True
        assert session.modified is True  # setdefault modifies the session

    def test_setdefault_existing_key_sets_accessed(self):
        """Test that setdefault with existing key sets accessed flag."""
        session = SecureCookieSession({"key": "existing_value"})
        
        # Reset accessed flag after initialization
        session.accessed = False
        
        # Access via setdefault with existing key
        value = session.setdefault("key", "new_value")
        
        assert value == "existing_value"
        assert session.accessed is True
        assert session.modified is False  # No modification when key exists

    def test_update_sets_modified_and_accessed(self):
        """Test that updating the session sets both modified and accessed flags."""
        session = SecureCookieSession()
        
        # Initially not modified or accessed
        assert session.modified is False
        assert session.accessed is False
        
        # Update the session
        session["new_key"] = "new_value"
        
        assert session.modified is True
        assert session.accessed is True
        assert session["new_key"] == "new_value"

    def test_multiple_operations(self):
        """Test multiple operations maintain correct flag states."""
        session = SecureCookieSession()
        
        # Initial state
        assert session.modified is False
        assert session.accessed is False
        
        # Read operation
        value = session.get("key", "default")
        assert value == "default"
        assert session.accessed is True
        assert session.modified is False
        
        # Reset for next test
        session.accessed = False
        
        # Write operation
        session["key"] = "value"
        assert session.modified is True
        assert session.accessed is True
