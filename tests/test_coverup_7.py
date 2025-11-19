# file: src/flask/src/flask/testing.py:135-183
# asked: {"lines": [135, 136, 155, 156, 157, 160, 161, 162, 164, 165, 167, 168, 170, 171, 173, 174, 176, 177, 179, 180, 181, 182], "branches": [[155, 156], [155, 160], [167, 168], [167, 170], [173, 174], [173, 176]]}
# gained: {"lines": [135, 136, 155, 156, 157, 160, 161, 162, 164, 165, 167, 168, 170, 171, 173, 176, 177, 179, 180, 181, 182], "branches": [[155, 156], [155, 160], [167, 168], [167, 170], [173, 176]]}

import pytest
from flask import Flask, session
from flask.testing import FlaskClient
from flask.sessions import SessionMixin

def test_session_transaction_with_null_session():
    """Test session_transaction when session_interface.is_null_session returns True"""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    # Create a custom session interface that returns a null session
    class NullSessionInterface:
        def open_session(self, app, request):
            return None
            
        def save_session(self, app, session, response):
            pass
            
        def is_null_session(self, session):
            return True
    
    app.session_interface = NullSessionInterface()
    
    with app.test_client(use_cookies=True) as client:
        with pytest.raises(RuntimeError, match="Session backend did not open a session."):
            with client.session_transaction():
                pass

def test_session_transaction_with_cookies_disabled():
    """Test session_transaction when cookies are disabled"""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    with app.test_client(use_cookies=False) as client:
        with pytest.raises(TypeError, match="Cookies are disabled. Create a client with 'use_cookies=True'."):
            with client.session_transaction():
                pass

def test_session_transaction_successful_flow():
    """Test successful session_transaction flow with session modification"""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    @app.route('/')
    def index():
        return 'Hello'
    
    with app.test_client(use_cookies=True) as client:
        with client.session_transaction() as sess:
            assert isinstance(sess, SessionMixin)
            sess['test_key'] = 'test_value'
        
        # Verify the session was saved by making a request that uses the session
        response = client.get('/')
        assert response.status_code == 200

def test_session_transaction_with_request_context_args():
    """Test session_transaction with additional request context arguments"""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    with app.test_client(use_cookies=True) as client:
        # Test with path argument
        with client.session_transaction(path='/test') as sess:
            sess['path_test'] = 'value'
        
        # Test with method argument
        with client.session_transaction(method='POST') as sess:
            sess['method_test'] = 'value'
        
        # Test with multiple arguments
        with client.session_transaction(path='/multi', method='GET', data={'key': 'value'}) as sess:
            sess['multi_test'] = 'value'

def test_session_transaction_nested():
    """Test nested session_transaction calls"""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    with app.test_client(use_cookies=True) as client:
        with client.session_transaction() as outer_sess:
            outer_sess['outer'] = 'outer_value'
            
            # Nested session transaction should work
            with client.session_transaction() as inner_sess:
                inner_sess['inner'] = 'inner_value'
            
            # Outer session should still be accessible
            assert outer_sess['outer'] == 'outer_value'
