# file: src/flask/src/flask/sessions.py:337-349
# asked: {"lines": [337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349], "branches": [[339, 340], [339, 341], [342, 343], [342, 344]]}
# gained: {"lines": [337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349], "branches": [[339, 340], [339, 341], [342, 343], [342, 344]]}

import pytest
from unittest.mock import Mock, patch
from datetime import timedelta
from itsdangerous import BadSignature, URLSafeTimedSerializer
from flask.sessions import SecureCookieSessionInterface, SecureCookieSession
from flask import Flask
from flask.wrappers import Request

class TestSecureCookieSessionInterface:
    
    def test_open_session_no_signing_serializer(self):
        """Test that open_session returns None when signing serializer is None"""
        app = Flask(__name__)
        request = Mock(spec=Request)
        request.cookies = {}
        
        interface = SecureCookieSessionInterface()
        
        with patch.object(interface, 'get_signing_serializer', return_value=None):
            result = interface.open_session(app, request)
            assert result is None
    
    def test_open_session_no_cookie_value(self):
        """Test that open_session returns empty session when no cookie value"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        request = Mock(spec=Request)
        request.cookies = {}
        
        interface = SecureCookieSessionInterface()
        
        with patch.object(interface, 'get_signing_serializer') as mock_serializer:
            mock_serializer.return_value = Mock(spec=URLSafeTimedSerializer)
            result = interface.open_session(app, request)
            
            assert isinstance(result, SecureCookieSession)
            assert len(result) == 0
    
    def test_open_session_bad_signature(self):
        """Test that open_session returns empty session when signature is invalid"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.permanent_session_lifetime = timedelta(hours=1)
        
        request = Mock(spec=Request)
        request.cookies = {'session': 'invalid-signed-data'}
        
        interface = SecureCookieSessionInterface()
        
        with patch.object(interface, 'get_signing_serializer') as mock_serializer:
            mock_s = Mock(spec=URLSafeTimedSerializer)
            mock_s.loads.side_effect = BadSignature('Invalid signature')
            mock_serializer.return_value = mock_s
            
            with patch.object(interface, 'get_cookie_name', return_value='session'):
                result = interface.open_session(app, request)
                
                assert isinstance(result, SecureCookieSession)
                assert len(result) == 0
                mock_s.loads.assert_called_once_with('invalid-signed-data', max_age=3600)
    
    def test_open_session_valid_session(self):
        """Test that open_session returns session with data when valid"""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.permanent_session_lifetime = timedelta(hours=1)
        
        request = Mock(spec=Request)
        request.cookies = {'session': 'valid-signed-data'}
        
        interface = SecureCookieSessionInterface()
        
        with patch.object(interface, 'get_signing_serializer') as mock_serializer:
            mock_s = Mock(spec=URLSafeTimedSerializer)
            mock_s.loads.return_value = {'user_id': 123, 'username': 'testuser'}
            mock_serializer.return_value = mock_s
            
            with patch.object(interface, 'get_cookie_name', return_value='session'):
                result = interface.open_session(app, request)
                
                assert isinstance(result, SecureCookieSession)
                assert result['user_id'] == 123
                assert result['username'] == 'testuser'
                mock_s.loads.assert_called_once_with('valid-signed-data', max_age=3600)
