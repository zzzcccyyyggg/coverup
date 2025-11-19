# file: src/flask/src/flask/ctx.py:338-347
# asked: {"lines": [338, 339, 345, 346, 347], "branches": []}
# gained: {"lines": [338, 339, 345, 346, 347], "branches": []}

import pytest
from flask import Flask
from flask.ctx import AppContext
from werkzeug.test import EnvironBuilder

class TestAppContextFromEnviron:
    def test_from_environ_creates_context_with_request(self):
        """Test that from_environ creates an AppContext with request data from WSGI environ."""
        app = Flask(__name__)
        
        # Create a WSGI environ using Werkzeug's EnvironBuilder
        builder = EnvironBuilder(method='GET', path='/test')
        environ = builder.get_environ()
        
        # Call the class method
        ctx = AppContext.from_environ(app, environ)
        
        # Verify the context was created with the correct app
        assert ctx.app is app
        
        # Verify the request was created from the environ
        assert ctx._request is not None
        assert ctx._request.environ is environ
        
        # Verify the request has the app's json module
        assert ctx._request.json_module is app.json
        
        # Verify the context has request data
        assert ctx.has_request is True

    def test_from_environ_with_different_environ_data(self):
        """Test from_environ with different WSGI environ configurations."""
        app = Flask(__name__)
        
        # Test with POST method and form data
        builder = EnvironBuilder(
            method='POST', 
            path='/submit',
            data={'key': 'value'}
        )
        environ = builder.get_environ()
        
        ctx = AppContext.from_environ(app, environ)
        
        assert ctx.app is app
        assert ctx._request is not None
        assert ctx._request.environ is environ
        assert ctx._request.method == 'POST'
        assert ctx._request.json_module is app.json
