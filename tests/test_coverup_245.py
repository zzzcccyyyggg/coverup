# file: src/flask/src/flask/app.py:1380-1394
# asked: {"lines": [1380, 1394], "branches": []}
# gained: {"lines": [1380, 1394], "branches": []}

import pytest
from flask import Flask
from flask.ctx import AppContext
from werkzeug.test import EnvironBuilder


class TestFlaskRequestContext:
    """Test cases for Flask.request_context method."""

    def test_request_context_creates_app_context_with_environ(self):
        """Test that request_context creates an AppContext with the given WSGI environment."""
        app = Flask(__name__)
        
        # Create a valid WSGI environment
        builder = EnvironBuilder(method='GET', path='/')
        environ = builder.get_environ()
        
        # Call request_context method
        ctx = app.request_context(environ)
        
        # Verify the returned object is an AppContext
        assert isinstance(ctx, AppContext)
        
        # Verify the AppContext has the correct app
        assert ctx.app is app
        
        # Verify the AppContext has a request object created from the environ
        assert ctx._request is not None
        assert ctx._request.environ is environ
        
        # Clean up
        builder.close()

    def test_request_context_with_different_environ_methods(self):
        """Test request_context with different HTTP methods in the environ."""
        app = Flask(__name__)
        
        # Test with POST method
        builder = EnvironBuilder(method='POST', path='/test', data={'key': 'value'})
        environ = builder.get_environ()
        
        ctx = app.request_context(environ)
        assert isinstance(ctx, AppContext)
        assert ctx._request.method == 'POST'
        
        builder.close()

    def test_request_context_with_query_string(self):
        """Test request_context with query parameters in the environ."""
        app = Flask(__name__)
        
        builder = EnvironBuilder(method='GET', path='/search', query_string={'q': 'flask'})
        environ = builder.get_environ()
        
        ctx = app.request_context(environ)
        assert isinstance(ctx, AppContext)
        assert ctx._request.args.get('q') == 'flask'
        
        builder.close()

    def test_request_context_with_headers(self):
        """Test request_context with custom headers in the environ."""
        app = Flask(__name__)
        
        builder = EnvironBuilder(
            method='GET', 
            path='/',
            headers={'Content-Type': 'application/json', 'X-Custom-Header': 'test'}
        )
        environ = builder.get_environ()
        
        ctx = app.request_context(environ)
        assert isinstance(ctx, AppContext)
        assert ctx._request.headers.get('Content-Type') == 'application/json'
        assert ctx._request.headers.get('X-Custom-Header') == 'test'
        
        builder.close()
