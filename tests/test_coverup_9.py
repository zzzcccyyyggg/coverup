# file: src/flask/src/flask/sessions.py:351-399
# asked: {"lines": [351, 354, 355, 356, 357, 358, 359, 360, 363, 364, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 379, 381, 383, 384, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 399], "branches": [[363, 364], [363, 368], [368, 369], [368, 383], [369, 370], [369, 381], [383, 384], [383, 386]]}
# gained: {"lines": [351, 354, 355, 356, 357, 358, 359, 360, 363, 364, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 379, 381, 383, 384, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 399], "branches": [[363, 364], [363, 368], [368, 369], [368, 383], [369, 370], [369, 381], [383, 384], [383, 386]]}

import pytest
from flask import Flask
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from flask.wrappers import Response
from unittest.mock import Mock, patch
from datetime import datetime

class MockSession(SessionMixin):
    def __init__(self, data=None, accessed=False, modified=False):
        self._data = data or {}
        self.accessed = accessed
        self.modified = modified
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
        self.modified = True
    
    def __delitem__(self, key):
        del self._data[key]
        self.modified = True
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)
    
    def __bool__(self):
        return bool(self._data)

class TestSecureCookieSessionInterface:
    def test_save_session_empty_modified(self):
        """Test save_session when session is empty and modified (lines 368-381)"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        response = Response()
        session = MockSession(accessed=True, modified=True)
        
        interface = SecureCookieSessionInterface()
        interface.save_session(app, session, response)
        
        assert 'Cookie' in response.vary
        # Should have called delete_cookie but we can't easily verify that without mocking
    
    def test_save_session_empty_not_modified(self):
        """Test save_session when session is empty and not modified (lines 368, 381)"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        response = Response()
        session = MockSession(accessed=True, modified=False)
        
        interface = SecureCookieSessionInterface()
        interface.save_session(app, session, response)
        
        assert 'Cookie' in response.vary
    
    def test_save_session_should_not_set_cookie(self):
        """Test save_session when should_set_cookie returns False (lines 383-384)"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        response = Response()
        session = MockSession({'key': 'value'}, accessed=True, modified=True)
        
        interface = SecureCookieSessionInterface()
        
        with patch.object(interface, 'should_set_cookie', return_value=False):
            interface.save_session(app, session, response)
        
        assert 'Cookie' in response.vary
    
    def test_save_session_full_path(self):
        """Test save_session full path with cookie setting (lines 386-399)"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        response = Response()
        session = MockSession({'key': 'value'}, accessed=True, modified=True)
        
        interface = SecureCookieSessionInterface()
        
        with patch.object(interface, 'should_set_cookie', return_value=True):
            with patch.object(interface, 'get_expiration_time', return_value=None):
                with patch.object(interface, 'get_signing_serializer') as mock_serializer:
                    mock_serializer.return_value.dumps.return_value = 'signed-value'
                    interface.save_session(app, session, response)
        
        assert 'Cookie' in response.vary
        mock_serializer.return_value.dumps.assert_called_once_with({'key': 'value'})
    
    def test_save_session_not_accessed(self):
        """Test save_session when session was not accessed (line 363)"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        response = Response()
        session = MockSession({'key': 'value'}, accessed=False, modified=True)
        
        interface = SecureCookieSessionInterface()
        
        with patch.object(interface, 'should_set_cookie', return_value=True):
            with patch.object(interface, 'get_expiration_time', return_value=None):
                with patch.object(interface, 'get_signing_serializer') as mock_serializer:
                    mock_serializer.return_value.dumps.return_value = 'signed-value'
                    interface.save_session(app, session, response)
        
        # Cookie should still be in vary because we set a cookie
        assert 'Cookie' in response.vary
