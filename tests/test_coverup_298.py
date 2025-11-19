# file: src/flask/src/flask/app.py:739-772
# asked: {"lines": [761, 767, 772], "branches": [[760, 761], [766, 767], [770, 772]]}
# gained: {"lines": [761, 767, 772], "branches": [[760, 761], [766, 767], [770, 772]]}

import pytest
from werkzeug.exceptions import HTTPException
from werkzeug.routing.exceptions import RoutingException
from flask import Flask
from unittest.mock import Mock, patch


class TestHTTPException(HTTPException):
    """Custom HTTPException with no code for testing"""
    code = None


class TestRoutingException(RoutingException, HTTPException):
    """Custom RoutingException for testing"""
    code = 301


def test_handle_http_exception_with_none_code():
    """Test that HTTPException with None code is returned unchanged (line 761)"""
    app = Flask(__name__)
    exception = TestHTTPException("Test exception with no code")
    
    result = app.handle_http_exception(exception)
    
    assert result is exception


def test_handle_http_exception_routing_exception():
    """Test that RoutingException is returned unchanged (line 767)"""
    app = Flask(__name__)
    exception = TestRoutingException("Test routing exception")
    
    result = app.handle_http_exception(exception)
    
    assert result is exception


def test_handle_http_exception_with_error_handler():
    """Test that HTTPException with error handler calls ensure_sync (line 772)"""
    app = Flask(__name__)
    
    # Create a mock HTTPException with a code
    class MockHTTPException(HTTPException):
        code = 404
    
    exception = MockHTTPException("Test exception")
    
    # Mock the error handler
    mock_handler = Mock(return_value="handled response")
    
    # Mock _find_error_handler to return our handler and mock request.blueprints
    with patch.object(app, '_find_error_handler', return_value=mock_handler):
        # Mock ensure_sync to return the handler directly
        with patch.object(app, 'ensure_sync', return_value=mock_handler):
            # Create a test request context to avoid the request context error
            with app.test_request_context():
                result = app.handle_http_exception(exception)
    
    # Verify the handler was called with the exception
    mock_handler.assert_called_once_with(exception)
    assert result == "handled response"
