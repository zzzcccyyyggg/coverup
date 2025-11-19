# file: src/flask/src/flask/app.py:1445-1491
# asked: {"lines": [1445, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1485, 1486, 1488, 1489, 1491], "branches": [[1485, 1486], [1485, 1488], [1488, 1489], [1488, 1491]]}
# gained: {"lines": [1445, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1485, 1486, 1488, 1489, 1491], "branches": [[1485, 1486], [1485, 1488], [1488, 1489], [1488, 1491]]}

import pytest
import sys
from unittest.mock import Mock, patch
from werkzeug.exceptions import InternalServerError
from flask import Flask
from flask.wrappers import Response


def test_wsgi_app_normal_execution():
    """Test normal execution path without exceptions."""
    app = Flask(__name__)
    
    # Mock the request context and response
    mock_ctx = Mock()
    mock_ctx.push = Mock()
    mock_ctx.pop = Mock()
    
    mock_response = Mock()
    mock_response.return_value = [b"test response"]
    
    with patch.object(app, 'request_context', return_value=mock_ctx):
        with patch.object(app, 'full_dispatch_request', return_value=mock_response):
            environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
            start_response = Mock()
            
            result = app.wsgi_app(environ, start_response)
            
            # Verify the normal execution flow
            mock_ctx.push.assert_called_once()
            mock_response.assert_called_once_with(environ, start_response)
            mock_ctx.pop.assert_called_once_with(None)
            assert result == [b"test response"]


def test_wsgi_app_with_exception_handled():
    """Test execution path when an exception occurs and is handled."""
    app = Flask(__name__)
    
    # Mock the request context and response
    mock_ctx = Mock()
    mock_ctx.push = Mock()
    mock_ctx.pop = Mock()
    
    mock_response = Mock()
    mock_response.return_value = [b"error response"]
    
    test_exception = Exception("Test error")
    
    with patch.object(app, 'request_context', return_value=mock_ctx):
        with patch.object(app, 'full_dispatch_request', side_effect=test_exception):
            with patch.object(app, 'handle_exception', return_value=mock_response):
                environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
                start_response = Mock()
                
                result = app.wsgi_app(environ, start_response)
                
                # Verify exception handling flow
                mock_ctx.push.assert_called_once()
                app.handle_exception.assert_called_once_with(test_exception)
                mock_response.assert_called_once_with(environ, start_response)
                mock_ctx.pop.assert_called_once_with(test_exception)
                assert result == [b"error response"]


def test_wsgi_app_with_ignored_error():
    """Test execution path when an error occurs but should be ignored."""
    app = Flask(__name__)
    
    # Mock the request context and response
    mock_ctx = Mock()
    mock_ctx.push = Mock()
    mock_ctx.pop = Mock()
    
    mock_response = Mock()
    mock_response.return_value = [b"error response"]
    
    test_exception = Exception("Test error")
    
    with patch.object(app, 'request_context', return_value=mock_ctx):
        with patch.object(app, 'full_dispatch_request', side_effect=test_exception):
            with patch.object(app, 'handle_exception', return_value=mock_response):
                with patch.object(app, 'should_ignore_error', return_value=True):
                    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
                    start_response = Mock()
                    
                    result = app.wsgi_app(environ, start_response)
                    
                    # Verify that error is set to None when should_ignore_error returns True
                    mock_ctx.pop.assert_called_once_with(None)
                    assert result == [b"error response"]


def test_wsgi_app_with_preserve_context():
    """Test execution path when werkzeug.debug.preserve_context is in environ."""
    app = Flask(__name__)
    
    # Mock the request context and response
    mock_ctx = Mock()
    mock_ctx.push = Mock()
    mock_ctx.pop = Mock()
    
    mock_response = Mock()
    mock_response.return_value = [b"test response"]
    
    mock_preserve_context = Mock()
    
    with patch.object(app, 'request_context', return_value=mock_ctx):
        with patch.object(app, 'full_dispatch_request', return_value=mock_response):
            environ = {
                'REQUEST_METHOD': 'GET', 
                'PATH_INFO': '/',
                'werkzeug.debug.preserve_context': mock_preserve_context
            }
            start_response = Mock()
            
            # Mock _cv_app.get() to return the app
            with patch('flask.app._cv_app') as mock_cv_app:
                mock_cv_app.get.return_value = app
                
                result = app.wsgi_app(environ, start_response)
                
                # Verify preserve_context is called with the app
                mock_preserve_context.assert_called_once_with(app)
                mock_ctx.pop.assert_called_once_with(None)
                assert result == [b"test response"]


def test_wsgi_app_with_base_exception():
    """Test execution path when a BaseException (non-Exception) occurs."""
    app = Flask(__name__)
    
    # Mock the request context
    mock_ctx = Mock()
    mock_ctx.push = Mock()
    mock_ctx.pop = Mock()
    
    test_exception = KeyboardInterrupt("Test interrupt")
    
    with patch.object(app, 'request_context', return_value=mock_ctx):
        with patch.object(app, 'full_dispatch_request', side_effect=test_exception):
            environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
            start_response = Mock()
            
            # This should re-raise the BaseException
            with pytest.raises(KeyboardInterrupt):
                app.wsgi_app(environ, start_response)
            
            # Verify that error was captured and ctx.pop was called with the error
            mock_ctx.pop.assert_called_once_with(test_exception)
