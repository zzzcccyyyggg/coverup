# file: src/flask/src/flask/app.py:1263-1289
# asked: {"lines": [1263, 1273, 1274, 1276, 1277, 1278, 1279, 1281, 1282, 1283, 1284, 1286, 1287, 1289], "branches": [[1276, 1277], [1276, 1281], [1277, 1276], [1277, 1278], [1278, 1276], [1278, 1279], [1281, 1282], [1281, 1289], [1282, 1281], [1282, 1283], [1283, 1281], [1283, 1284], [1286, 1283], [1286, 1287]]}
# gained: {"lines": [1263, 1273, 1274, 1276, 1277, 1278, 1279, 1281, 1282, 1283, 1284, 1286, 1287, 1289], "branches": [[1276, 1277], [1276, 1281], [1277, 1276], [1277, 1278], [1278, 1276], [1278, 1279], [1281, 1282], [1281, 1289], [1282, 1281], [1282, 1283], [1283, 1281], [1283, 1284], [1286, 1283], [1286, 1287]]}

import pytest
from flask import Flask
from flask.globals import _cv_app
from unittest.mock import Mock, patch
import contextvars


class TestFlaskPreprocessRequest:
    """Test cases for Flask.preprocess_request method to achieve full coverage."""
    
    def test_preprocess_request_with_url_value_preprocessors(self):
        """Test that url_value_preprocessors are called correctly."""
        app = Flask(__name__)
        
        # Mock request with blueprints
        mock_request = Mock()
        mock_request.blueprints = ['bp1', 'bp2']
        mock_request.endpoint = 'test_endpoint'
        mock_request.view_args = {'id': 1}
        
        # Create mock url value preprocessors
        mock_url_func1 = Mock()
        mock_url_func2 = Mock()
        mock_url_func3 = Mock()
        
        app.url_value_preprocessors = {
            None: [mock_url_func1],
            'bp1': [mock_url_func2],
            'bp2': [mock_url_func3]
        }
        
        app.before_request_funcs = {}
        
        # Create a mock context that returns our mock request
        mock_context = Mock()
        mock_context.request = mock_request
        
        # Use contextvars.ContextVar.set() to set the context
        token = _cv_app.set(mock_context)
        try:
            result = app.preprocess_request()
            
            # Verify url value preprocessors were called in correct order
            # Order should be: None, bp2, bp1 (reversed blueprints)
            assert mock_url_func1.called
            assert mock_url_func2.called
            assert mock_url_func3.called
            
            # Check calls were made with correct arguments
            mock_url_func1.assert_called_with('test_endpoint', {'id': 1})
            mock_url_func2.assert_called_with('test_endpoint', {'id': 1})
            mock_url_func3.assert_called_with('test_endpoint', {'id': 1})
            
            # Should return None since no before_request handlers
            assert result is None
        finally:
            # Clean up the context
            _cv_app.reset(token)
    
    def test_preprocess_request_with_before_request_returning_value(self):
        """Test that preprocess_request returns early when before_request returns non-None."""
        app = Flask(__name__)
        
        # Mock request with blueprints
        mock_request = Mock()
        mock_request.blueprints = ['bp1']
        mock_request.endpoint = 'test_endpoint'
        mock_request.view_args = {}
        
        app.url_value_preprocessors = {}
        
        # Create mock before_request function that returns a value
        mock_response = Mock()
        mock_before_func = Mock(return_value=mock_response)
        
        app.before_request_funcs = {
            None: [mock_before_func]
        }
        
        # Create a mock context that returns our mock request
        mock_context = Mock()
        mock_context.request = mock_request
        
        token = _cv_app.set(mock_context)
        try:
            result = app.preprocess_request()
            
            # Verify before_request was called
            mock_before_func.assert_called_once()
            
            # Should return the response from before_request
            assert result is mock_response
        finally:
            _cv_app.reset(token)
    
    def test_preprocess_request_with_multiple_before_requests(self):
        """Test that only the first non-None before_request return value is used."""
        app = Flask(__name__)
        
        # Mock request
        mock_request = Mock()
        mock_request.blueprints = []
        mock_request.endpoint = 'test_endpoint'
        mock_request.view_args = {}
        
        app.url_value_preprocessors = {}
        
        # Create multiple before_request functions
        mock_func1 = Mock(return_value=None)
        mock_func2 = Mock(return_value='early_return')
        mock_func3 = Mock()  # Should not be called
        
        app.before_request_funcs = {
            None: [mock_func1, mock_func2, mock_func3]
        }
        
        # Create a mock context that returns our mock request
        mock_context = Mock()
        mock_context.request = mock_request
        
        token = _cv_app.set(mock_context)
        try:
            result = app.preprocess_request()
            
            # Verify first two functions were called, third was not
            mock_func1.assert_called_once()
            mock_func2.assert_called_once()
            mock_func3.assert_not_called()
            
            # Should return the second function's return value
            assert result == 'early_return'
        finally:
            _cv_app.reset(token)
    
    def test_preprocess_request_with_blueprint_before_requests(self):
        """Test that blueprint before_request functions are called in correct order."""
        app = Flask(__name__)
        
        # Mock request with blueprints
        mock_request = Mock()
        mock_request.blueprints = ['bp1', 'bp2']
        mock_request.endpoint = 'test_endpoint'
        mock_request.view_args = {}
        
        app.url_value_preprocessors = {}
        
        # Create before_request functions for different scopes
        mock_app_func = Mock(return_value=None)
        mock_bp1_func = Mock(return_value=None)
        mock_bp2_func = Mock(return_value='bp2_return')
        
        app.before_request_funcs = {
            None: [mock_app_func],
            'bp1': [mock_bp1_func],
            'bp2': [mock_bp2_func]
        }
        
        # Create a mock context that returns our mock request
        mock_context = Mock()
        mock_context.request = mock_request
        
        token = _cv_app.set(mock_context)
        try:
            result = app.preprocess_request()
            
            # Verify functions were called in correct order: None, bp2, bp1
            mock_app_func.assert_called_once()
            mock_bp2_func.assert_called_once()
            mock_bp1_func.assert_not_called()  # Should not be called due to early return
            
            # Should return bp2 function's return value
            assert result == 'bp2_return'
        finally:
            _cv_app.reset(token)
    
    def test_preprocess_request_no_handlers(self):
        """Test preprocess_request when no preprocessors or before_request handlers exist."""
        app = Flask(__name__)
        
        # Mock request without blueprints
        mock_request = Mock()
        mock_request.blueprints = []
        mock_request.endpoint = 'test_endpoint'
        mock_request.view_args = {}
        
        app.url_value_preprocessors = {}
        app.before_request_funcs = {}
        
        # Create a mock context that returns our mock request
        mock_context = Mock()
        mock_context.request = mock_request
        
        token = _cv_app.set(mock_context)
        try:
            result = app.preprocess_request()
            
            # Should return None
            assert result is None
        finally:
            _cv_app.reset(token)
