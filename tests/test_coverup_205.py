# file: src/flask/src/flask/ctx.py:398-407
# asked: {"lines": [398, 402, 403, 404, 405, 407], "branches": []}
# gained: {"lines": [398, 402, 403, 404, 405, 407], "branches": []}

import pytest
from werkzeug.exceptions import HTTPException
from werkzeug.routing import MapAdapter, Rule
from flask import Flask
from flask.ctx import AppContext
from flask.wrappers import Request

class MockMapAdapter:
    """Mock MapAdapter that can simulate both successful matches and exceptions."""
    def __init__(self, should_raise=False, exception=None, match_result=None):
        self.should_raise = should_raise
        self.exception = exception
        self.match_result = match_result
    
    def match(self, return_rule=True):
        if self.should_raise:
            raise self.exception
        return self.match_result

def test_match_request_successful_match():
    """Test match_request when URL adapter successfully matches a route."""
    app = Flask(__name__)
    
    # Create a mock rule and view args for successful match
    mock_rule = Rule('/test', endpoint='test_endpoint')
    mock_view_args = {'param': 'value'}
    match_result = (mock_rule, mock_view_args)
    
    # Create AppContext with request using proper WSGI environment
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/test',
        'wsgi.url_scheme': 'http',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '5000'
    }
    request = Request(environ)
    ctx = AppContext(app, request=request)
    
    # Mock the url_adapter to return successful match
    ctx.url_adapter = MockMapAdapter(
        should_raise=False,
        match_result=match_result
    )
    
    # Execute the method under test
    ctx.match_request()
    
    # Verify the request was updated with the matched rule and view args
    assert ctx._request.url_rule == mock_rule
    assert ctx._request.view_args == mock_view_args
    assert ctx._request.routing_exception is None

def test_match_request_http_exception():
    """Test match_request when URL adapter raises HTTPException."""
    app = Flask(__name__)
    
    # Create AppContext with request using proper WSGI environment
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/nonexistent',
        'wsgi.url_scheme': 'http',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '5000'
    }
    request = Request(environ)
    ctx = AppContext(app, request=request)
    
    # Create a mock HTTPException
    http_exception = HTTPException("Not Found")
    
    # Mock the url_adapter to raise HTTPException
    ctx.url_adapter = MockMapAdapter(
        should_raise=True,
        exception=http_exception
    )
    
    # Execute the method under test
    ctx.match_request()
    
    # Verify the request stores the routing exception
    assert ctx._request.routing_exception == http_exception
    assert ctx._request.url_rule is None
    assert ctx._request.view_args is None

def test_match_request_no_url_adapter():
    """Test match_request when url_adapter is None - should raise AttributeError."""
    app = Flask(__name__)
    
    # Create AppContext with request using proper WSGI environment
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/test',
        'wsgi.url_scheme': 'http',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '5000'
    }
    request = Request(environ)
    ctx = AppContext(app, request=request)
    
    # Set url_adapter to None
    ctx.url_adapter = None
    
    # This should raise AttributeError when trying to call match() on None
    with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'match'"):
        ctx.match_request()
    
    # Verify no changes to request (since the method failed)
    assert ctx._request.url_rule is None
    assert ctx._request.view_args is None
    assert ctx._request.routing_exception is None
