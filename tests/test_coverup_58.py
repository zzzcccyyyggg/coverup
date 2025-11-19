# file: src/flask/src/flask/testing.py:204-247
# asked: {"lines": [204, 207, 208, 211, 212, 214, 215, 216, 217, 218, 219, 220, 221, 224, 225, 228, 233, 235, 236, 237, 238, 240, 243, 244, 246, 247], "branches": [[211, 214], [211, 228], [214, 215], [214, 218], [218, 219], [218, 224], [243, 244], [243, 246]]}
# gained: {"lines": [204, 207, 208, 211, 212, 214, 215, 216, 217, 218, 219, 220, 221, 224, 225, 228, 233, 235, 236, 237, 238, 240, 243, 244, 246, 247], "branches": [[211, 214], [211, 228], [214, 215], [214, 218], [218, 219], [218, 224], [243, 244], [243, 246]]}

import pytest
import werkzeug.test
from werkzeug.wrappers import Request as BaseRequest
from flask import Flask
from flask.testing import FlaskClient


@pytest.fixture
def app():
    """Create a Flask application for testing."""
    app = Flask(__name__)
    return app


class TestFlaskClientOpen:
    """Test cases for FlaskClient.open method to achieve full coverage."""
    
    def test_open_with_environ_builder(self, app):
        """Test open method with EnvironBuilder as first argument."""
        client = app.test_client()
        builder = werkzeug.test.EnvironBuilder(path='/test', method='GET')
        
        response = client.open(builder)
        
        assert response.status_code == 404  # Default for non-existent route
    
    def test_open_with_dict_environ(self, app):
        """Test open method with dict environ as first argument."""
        client = app.test_client()
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/test',
            'SCRIPT_NAME': '',
            'QUERY_STRING': '',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'HTTP_HOST': 'localhost:5000',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': None,
            'wsgi.errors': None,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        response = client.open(environ)
        
        assert response.status_code == 404  # Default for non-existent route
    
    def test_open_with_base_request(self, app):
        """Test open method with BaseRequest as first argument."""
        client = app.test_client()
        
        # Create a simple BaseRequest
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/test',
            'SCRIPT_NAME': '',
            'QUERY_STRING': '',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'HTTP_HOST': 'localhost:5000',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': None,
            'wsgi.errors': None,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        request = BaseRequest(environ)
        
        response = client.open(request)
        
        assert response.status_code == 404  # Default for non-existent route
    
    def test_open_with_regular_args(self, app):
        """Test open method with regular path/method arguments."""
        client = app.test_client()
        
        response = client.open('/test', method='GET')
        
        assert response.status_code == 404  # Default for non-existent route
    
    def test_open_with_buffered_true(self, app):
        """Test open method with buffered=True."""
        client = app.test_client()
        
        response = client.open('/test', method='GET', buffered=True)
        
        assert response.status_code == 404
        assert hasattr(response, 'data')
    
    def test_open_with_follow_redirects_true(self, app):
        """Test open method with follow_redirects=True."""
        client = app.test_client()
        
        @app.route('/redirect')
        def redirect_route():
            from flask import redirect
            return redirect('/target')
        
        @app.route('/target')
        def target_route():
            return 'Target reached'
        
        response = client.open('/redirect', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Target reached' in response.data
    
    def test_open_preserves_context_stack_cleanup(self, app):
        """Test that context stack is properly cleaned up and restored."""
        client = app.test_client()
        
        # Mock the context stack to verify it's closed
        original_close = client._context_stack.close
        close_called = False
        
        def mock_close():
            nonlocal close_called
            close_called = True
            original_close()
        
        client._context_stack.close = mock_close
        
        response = client.open('/test', method='GET')
        
        assert close_called
        assert response.status_code == 404
    
    def test_open_with_json_module_assignment(self, app):
        """Test that response.json_module is assigned from app.json."""
        client = app.test_client()
        
        response = client.open('/test', method='GET')
        
        assert response.json_module is app.json
    
    def test_open_with_new_contexts_restoration(self, app):
        """Test that new contexts are properly restored after request."""
        client = app.test_client()
        
        # Add a mock context manager to _new_contexts
        entered_contexts = []
        
        class MockContextManager:
            def __enter__(self):
                entered_contexts.append('entered')
                return self
            
            def __exit__(self, *args):
                entered_contexts.append('exited')
        
        client._new_contexts = [MockContextManager()]
        
        response = client.open('/test', method='GET')
        
        # Context should have been entered via the stack
        assert len(entered_contexts) >= 1
        assert client._new_contexts == []  # Should be cleared after request
        assert response.status_code == 404
