# file: src/flask/src/flask/logging.py:15-28
# asked: {"lines": [15, 16, 25, 26, 28], "branches": [[25, 26], [25, 28]]}
# gained: {"lines": [15, 16, 25, 26, 28], "branches": [[25, 26], [25, 28]]}

import pytest
import sys
from flask import Flask
from flask.logging import wsgi_errors_stream
from werkzeug.local import LocalProxy

def test_wsgi_errors_stream_without_request():
    """Test wsgi_errors_stream when no request is active (returns sys.stderr)"""
    # When no request context is active, wsgi_errors_stream should return sys.stderr
    # We need to call _get_current_object() to get the actual value from the LocalProxy
    assert wsgi_errors_stream._get_current_object() is sys.stderr

def test_wsgi_errors_stream_with_request():
    """Test wsgi_errors_stream when a request is active (returns request.environ['wsgi.errors'])"""
    app = Flask(__name__)
    
    with app.test_request_context():
        # Create a mock wsgi.errors stream
        mock_errors_stream = object()
        
        # Patch the request.environ to include our mock wsgi.errors
        from flask import request
        request.environ['wsgi.errors'] = mock_errors_stream
        
        # Verify that wsgi_errors_stream returns our mock stream
        assert wsgi_errors_stream._get_current_object() is mock_errors_stream

def test_wsgi_errors_stream_is_local_proxy():
    """Verify that wsgi_errors_stream is indeed a LocalProxy instance"""
    assert isinstance(wsgi_errors_stream, LocalProxy)
