# file: src/flask/src/flask/sessions.py:24-49
# asked: {"lines": [24, 25, 27, 28, 30, 32, 33, 34, 39, 44, 49], "branches": []}
# gained: {"lines": [24, 25, 27, 28, 30, 32, 33, 34, 39, 44, 49], "branches": []}

import pytest
from flask.sessions import SessionMixin
from collections.abc import MutableMapping
from typing import Any, Dict

class TestSessionMixin:
    """Test cases for SessionMixin class to achieve full coverage."""
    
    def test_permanent_property_default_false(self):
        """Test that permanent property returns False by default."""
        class TestSession(SessionMixin):
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
                
            def get(self, key, default=None):
                return self._data.get(key, default)
        
        session = TestSession()
        assert session.permanent is False
    
    def test_permanent_property_with_permanent_key(self):
        """Test that permanent property returns value from '_permanent' key."""
        class TestSession(SessionMixin):
            def __init__(self):
                self._data = {"_permanent": True}
            
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
                
            def get(self, key, default=None):
                return self._data.get(key, default)
        
        session = TestSession()
        assert session.permanent is True
    
    def test_permanent_setter(self):
        """Test that permanent setter correctly sets '_permanent' key."""
        class TestSession(SessionMixin):
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
                
            def get(self, key, default=None):
                return self._data.get(key, default)
        
        session = TestSession()
        session.permanent = True
        assert session["_permanent"] is True
        
        session.permanent = False
        assert session["_permanent"] is False
    
    def test_default_attributes(self):
        """Test that default attributes are set correctly."""
        class TestSession(SessionMixin):
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
                
            def get(self, key, default=None):
                return self._data.get(key, default)
        
        session = TestSession()
        assert session.new is False
        assert session.modified is True
        assert session.accessed is True
