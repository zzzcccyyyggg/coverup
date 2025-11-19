# file: src/flask/src/flask/app.py:918-947
# asked: {"lines": [918, 921, 935, 936, 937, 938, 939, 941, 942, 943, 944, 945, 947], "branches": [[942, 943], [942, 944]]}
# gained: {"lines": [918, 921, 935, 936, 937, 938, 939, 941, 942, 943, 944, 945, 947], "branches": [[942, 943], [942, 944]]}

import pytest
from werkzeug.exceptions import HTTPException
from flask import Flask, Response
from flask.signals import request_finished
from unittest.mock import Mock, patch


class TestFlaskFinalizeRequest:
    """Test cases for Flask.finalize_request method to achieve full coverage."""
    
    def test_finalize_request_normal_flow(self):
        """Test normal flow of finalize_request without errors."""
        app = Flask(__name__)
        
        # Create a simple response
        test_response = Response("test")
        
        # Mock process_response to return the same response
        with patch.object(app, 'process_response', return_value=test_response):
            # Mock request_finished.send to track if it was called
            with patch.object(request_finished, 'send') as mock_send:
                result = app.finalize_request(test_response)
                
                # Verify the response is returned
                assert result == test_response
                # Verify process_response was called
                app.process_response.assert_called_once_with(test_response)
                # Verify request_finished.send was called
                mock_send.assert_called_once_with(
                    app, _async_wrapper=app.ensure_sync, response=test_response
                )
    
    def test_finalize_request_with_error_handler_false_and_exception(self):
        """Test finalize_request when exception occurs and from_error_handler=False."""
        app = Flask(__name__)
        
        # Create a simple response
        test_response = Response("test")
        
        # Mock process_response to raise an exception
        with patch.object(app, 'process_response', side_effect=Exception("Test error")):
            # Test that the exception is raised when from_error_handler=False
            with pytest.raises(Exception, match="Test error"):
                app.finalize_request(test_response, from_error_handler=False)
    
    def test_finalize_request_with_error_handler_true_and_exception(self):
        """Test finalize_request when exception occurs and from_error_handler=True."""
        app = Flask(__name__)
        
        # Create a simple response
        test_response = Response("test")
        
        # Mock process_response to raise an exception
        with patch.object(app, 'process_response', side_effect=Exception("Test error")):
            # Mock logger to track if exception was logged
            with patch.object(app, 'logger') as mock_logger:
                result = app.finalize_request(test_response, from_error_handler=True)
                
                # Verify the original response is still returned despite the exception
                assert result == test_response
                # Verify logger.exception was called with the expected message
                mock_logger.exception.assert_called_once_with(
                    "Request finalizing failed with an error while handling an error"
                )
    
    def test_finalize_request_with_http_exception(self):
        """Test finalize_request with HTTPException as return value."""
        app = Flask(__name__)
        
        # Create an HTTPException
        http_exception = HTTPException("Test HTTP exception")
        
        # Mock make_response to handle HTTPException
        with patch.object(app, 'make_response') as mock_make_response:
            mock_response = Response("converted response")
            mock_make_response.return_value = mock_response
            
            with patch.object(app, 'process_response', return_value=mock_response):
                with patch.object(request_finished, 'send'):
                    result = app.finalize_request(http_exception)
                    
                    # Verify make_response was called with the HTTPException
                    mock_make_response.assert_called_once_with(http_exception)
                    # Verify the processed response is returned
                    assert result == mock_response
    
    def test_finalize_request_with_tuple_response(self):
        """Test finalize_request with tuple response value."""
        app = Flask(__name__)
        
        # Create a tuple response (body, status, headers)
        tuple_response = ("test body", 200, {"X-Test": "value"})
        
        # Mock make_response to handle the tuple
        with patch.object(app, 'make_response') as mock_make_response:
            mock_converted_response = Response("converted response")
            mock_make_response.return_value = mock_converted_response
            
            with patch.object(app, 'process_response', return_value=mock_converted_response):
                with patch.object(request_finished, 'send'):
                    result = app.finalize_request(tuple_response)
                    
                    # Verify make_response was called with the tuple
                    mock_make_response.assert_called_once_with(tuple_response)
                    # Verify the processed response is returned
                    assert result == mock_converted_response
