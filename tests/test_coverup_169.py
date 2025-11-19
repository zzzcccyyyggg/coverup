# file: src/flask/src/flask/ctx.py:354-367
# asked: {"lines": [354, 363, 364, 365, 366], "branches": []}
# gained: {"lines": [354, 363, 364, 365, 366], "branches": []}

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.wrappers import Request
from flask.sessions import SessionMixin
from collections.abc import MutableMapping

class MockSession(MutableMapping):
    def __init__(self, data=None):
        self._data = data or {}
    
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
    
    @property
    def permanent(self):
        return False
    
    @permanent.setter
    def permanent(self, value):
        pass
    
    new = False
    modified = True
    accessed = True

class TestAppContextCopy:
    def test_copy_with_request_and_session(self):
        """Test that copy() creates a new context with the same request and session."""
        app = Flask(__name__)
        request = Request.from_values()
        session = MockSession({'test': 'data'})
        
        original_ctx = AppContext(app, request=request, session=session)
        copied_ctx = original_ctx.copy()
        
        assert copied_ctx is not original_ctx
        assert isinstance(copied_ctx, AppContext)
        assert copied_ctx.app is original_ctx.app
        assert copied_ctx._request is original_ctx._request
        assert copied_ctx._session is original_ctx._session

    def test_copy_without_request_and_session(self):
        """Test that copy() works when request and session are None."""
        app = Flask(__name__)
        
        original_ctx = AppContext(app)
        copied_ctx = original_ctx.copy()
        
        assert copied_ctx is not original_ctx
        assert isinstance(copied_ctx, AppContext)
        assert copied_ctx.app is original_ctx.app
        assert copied_ctx._request is None
        assert copied_ctx._session is None
