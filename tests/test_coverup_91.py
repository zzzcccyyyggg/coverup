# file: src/flask/src/flask/app.py:900-916
# asked: {"lines": [900, 907, 909, 910, 911, 912, 913, 914, 915, 916], "branches": [[912, 913], [912, 916]]}
# gained: {"lines": [900, 907, 909, 910, 911, 912, 913, 914, 915, 916], "branches": [[912, 913], [912, 916]]}

import pytest
from flask import Flask
from werkzeug.exceptions import InternalServerError
from unittest.mock import Mock, patch

class TestFlaskFullDispatchRequest:
    """Test cases for Flask.full_dispatch_request method to achieve full coverage."""
    
    def test_full_dispatch_request_normal_flow(self, monkeypatch):
        """Test the normal flow where preprocess_request returns None and dispatch_request succeeds."""
        app = Flask(__name__)
        
        # Mock the required methods
        mock_request_started_send = Mock()
        mock_preprocess_request = Mock(return_value=None)
        mock_dispatch_request = Mock(return_value="test_response")
        mock_finalize_request = Mock(return_value="final_response")
        
        # Patch the methods
        monkeypatch.setattr('flask.signals.request_started.send', mock_request_started_send)
        monkeypatch.setattr(app, 'preprocess_request', mock_preprocess_request)
        monkeypatch.setattr(app, 'dispatch_request', mock_dispatch_request)
        monkeypatch.setattr(app, 'finalize_request', mock_finalize_request)
        
        # Execute the method
        result = app.full_dispatch_request()
        
        # Verify the flow
        assert result == "final_response"
        mock_request_started_send.assert_called_once_with(app, _async_wrapper=app.ensure_sync)
        mock_preprocess_request.assert_called_once()
        mock_dispatch_request.assert_called_once()
        mock_finalize_request.assert_called_once_with("test_response")
        assert app._got_first_request is True
    
    def test_full_dispatch_request_preprocess_returns_value(self, monkeypatch):
        """Test the flow where preprocess_request returns a non-None value."""
        app = Flask(__name__)
        
        # Mock the required methods
        mock_request_started_send = Mock()
        mock_preprocess_request = Mock(return_value="preprocessed_response")
        mock_dispatch_request = Mock()
        mock_finalize_request = Mock(return_value="final_response")
        
        # Patch the methods
        monkeypatch.setattr('flask.signals.request_started.send', mock_request_started_send)
        monkeypatch.setattr(app, 'preprocess_request', mock_preprocess_request)
        monkeypatch.setattr(app, 'dispatch_request', mock_dispatch_request)
        monkeypatch.setattr(app, 'finalize_request', mock_finalize_request)
        
        # Execute the method
        result = app.full_dispatch_request()
        
        # Verify the flow
        assert result == "final_response"
        mock_request_started_send.assert_called_once_with(app, _async_wrapper=app.ensure_sync)
        mock_preprocess_request.assert_called_once()
        mock_dispatch_request.assert_not_called()  # Should not be called when preprocess returns value
        mock_finalize_request.assert_called_once_with("preprocessed_response")
        assert app._got_first_request is True
    
    def test_full_dispatch_request_with_exception(self, monkeypatch):
        """Test the flow where an exception occurs and is handled by handle_user_exception."""
        app = Flask(__name__)
        
        # Create a test exception
        test_exception = ValueError("Test error")
        
        # Mock the required methods
        mock_request_started_send = Mock()
        mock_preprocess_request = Mock(side_effect=test_exception)
        mock_dispatch_request = Mock()
        mock_handle_user_exception = Mock(return_value="handled_response")
        mock_finalize_request = Mock(return_value="final_response")
        
        # Patch the methods
        monkeypatch.setattr('flask.signals.request_started.send', mock_request_started_send)
        monkeypatch.setattr(app, 'preprocess_request', mock_preprocess_request)
        monkeypatch.setattr(app, 'dispatch_request', mock_dispatch_request)
        monkeypatch.setattr(app, 'handle_user_exception', mock_handle_user_exception)
        monkeypatch.setattr(app, 'finalize_request', mock_finalize_request)
        
        # Execute the method
        result = app.full_dispatch_request()
        
        # Verify the flow
        assert result == "final_response"
        mock_request_started_send.assert_called_once_with(app, _async_wrapper=app.ensure_sync)
        mock_preprocess_request.assert_called_once()
        mock_dispatch_request.assert_not_called()  # Should not be called when exception occurs
        mock_handle_user_exception.assert_called_once_with(test_exception)
        mock_finalize_request.assert_called_once_with("handled_response")
        assert app._got_first_request is True
    
    def test_full_dispatch_request_exception_in_request_started(self, monkeypatch):
        """Test the flow where an exception occurs in request_started.send."""
        app = Flask(__name__)
        
        # Create a test exception
        test_exception = RuntimeError("Signal error")
        
        # Mock the required methods
        mock_request_started_send = Mock(side_effect=test_exception)
        mock_preprocess_request = Mock()
        mock_dispatch_request = Mock()
        mock_handle_user_exception = Mock(return_value="handled_response")
        mock_finalize_request = Mock(return_value="final_response")
        
        # Patch the methods
        monkeypatch.setattr('flask.signals.request_started.send', mock_request_started_send)
        monkeypatch.setattr(app, 'preprocess_request', mock_preprocess_request)
        monkeypatch.setattr(app, 'dispatch_request', mock_dispatch_request)
        monkeypatch.setattr(app, 'handle_user_exception', mock_handle_user_exception)
        monkeypatch.setattr(app, 'finalize_request', mock_finalize_request)
        
        # Execute the method
        result = app.full_dispatch_request()
        
        # Verify the flow
        assert result == "final_response"
        mock_request_started_send.assert_called_once_with(app, _async_wrapper=app.ensure_sync)
        mock_preprocess_request.assert_not_called()  # Should not be called when exception occurs in signal
        mock_dispatch_request.assert_not_called()  # Should not be called when exception occurs
        mock_handle_user_exception.assert_called_once_with(test_exception)
        mock_finalize_request.assert_called_once_with("handled_response")
        assert app._got_first_request is True
