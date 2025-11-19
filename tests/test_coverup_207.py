# file: src/flask/src/flask/app.py:859-872
# asked: {"lines": [859, 870, 871], "branches": []}
# gained: {"lines": [859, 870, 871], "branches": []}

import pytest
from flask import Flask
from unittest.mock import Mock, patch
import sys
from types import TracebackType

class TestFlaskLogException:
    
    def test_log_exception_with_exception_info(self):
        """Test that log_exception logs error with exception info when exc_info is provided."""
        app = Flask(__name__)
        
        # Create a mock exception info tuple
        exc_type = ValueError
        exc_value = ValueError("Test error")
        try:
            raise exc_value
        except ValueError:
            exc_info = sys.exc_info()
        
        # Mock the logger.error method
        with patch.object(app.logger, 'error') as mock_error:
            # Mock request context
            with app.test_request_context('/test-path', method='POST'):
                app.log_exception(exc_info)
                
                # Verify the logger was called with the correct message and exc_info
                mock_error.assert_called_once()
                call_args = mock_error.call_args
                assert "Exception on /test-path [POST]" in call_args[0][0]
                assert call_args[1]['exc_info'] == exc_info
    
    def test_log_exception_with_none_exc_info(self):
        """Test that log_exception logs error when exc_info is (None, None, None)."""
        app = Flask(__name__)
        
        # Mock the logger.error method
        with patch.object(app.logger, 'error') as mock_error:
            # Mock request context
            with app.test_request_context('/another-path', method='GET'):
                app.log_exception((None, None, None))
                
                # Verify the logger was called with the correct message and None exc_info
                mock_error.assert_called_once()
                call_args = mock_error.call_args
                assert "Exception on /another-path [GET]" in call_args[0][0]
                assert call_args[1]['exc_info'] == (None, None, None)
    
    def test_log_exception_different_request_methods_and_paths(self):
        """Test log_exception with various HTTP methods and paths."""
        app = Flask(__name__)
        
        test_cases = [
            ('/api/users', 'GET'),
            ('/api/users/123', 'PUT'), 
            ('/api/users/123', 'DELETE'),
            ('/login', 'POST'),
            ('/static/style.css', 'GET')
        ]
        
        for path, method in test_cases:
            with patch.object(app.logger, 'error') as mock_error:
                with app.test_request_context(path, method=method):
                    exc_info = (ValueError, ValueError("Test"), None)
                    app.log_exception(exc_info)
                    
                    # Verify the message contains the correct path and method
                    call_args = mock_error.call_args
                    assert f"Exception on {path} [{method}]" in call_args[0][0]
                    assert call_args[1]['exc_info'] == exc_info
