# file: src/flask/src/flask/sessions.py:201-207
# asked: {"lines": [201, 207], "branches": []}
# gained: {"lines": [201, 207], "branches": []}

import pytest
from flask import Flask
from flask.sessions import SessionInterface

class TestSessionInterfaceGetCookiePath:
    """Test cases for SessionInterface.get_cookie_path method"""
    
    def test_get_cookie_path_with_session_cookie_path(self):
        """Test get_cookie_path when SESSION_COOKIE_PATH is set"""
        app = Flask(__name__)
        app.config['SESSION_COOKIE_PATH'] = '/custom'
        app.config['APPLICATION_ROOT'] = '/app'
        
        interface = SessionInterface()
        result = interface.get_cookie_path(app)
        
        assert result == '/custom'
    
    def test_get_cookie_path_without_session_cookie_path(self):
        """Test get_cookie_path when SESSION_COOKIE_PATH is not set"""
        app = Flask(__name__)
        app.config['SESSION_COOKIE_PATH'] = None
        app.config['APPLICATION_ROOT'] = '/app'
        
        interface = SessionInterface()
        result = interface.get_cookie_path(app)
        
        assert result == '/app'
    
    def test_get_cookie_path_with_empty_session_cookie_path(self):
        """Test get_cookie_path when SESSION_COOKIE_PATH is empty string"""
        app = Flask(__name__)
        app.config['SESSION_COOKIE_PATH'] = ''
        app.config['APPLICATION_ROOT'] = '/app'
        
        interface = SessionInterface()
        result = interface.get_cookie_path(app)
        
        assert result == '/app'
    
    def test_get_cookie_path_with_none_application_root(self):
        """Test get_cookie_path when both SESSION_COOKIE_PATH and APPLICATION_ROOT are None"""
        app = Flask(__name__)
        app.config['SESSION_COOKIE_PATH'] = None
        app.config['APPLICATION_ROOT'] = None
        
        interface = SessionInterface()
        result = interface.get_cookie_path(app)
        
        assert result is None
