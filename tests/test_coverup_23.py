# file: src/flask/src/flask/ctx.py:299-336
# asked: {"lines": [299, 303, 304, 306, 307, 311, 312, 314, 315, 319, 320, 321, 322, 324, 325, 326, 327, 328, 330, 331, 333, 334], "branches": [[327, 328], [327, 330]]}
# gained: {"lines": [299, 303, 304, 306, 307, 311, 312, 314, 315, 319, 320, 321, 322, 324, 325, 326, 327, 328, 330, 331, 333, 334], "branches": [[327, 328], [327, 330]]}

import pytest
from unittest.mock import Mock, patch
from werkzeug.exceptions import HTTPException
from flask import Flask
from flask.ctx import AppContext
from flask.wrappers import Request

class TestAppContextInit:
    """Test cases for AppContext.__init__ method to achieve full coverage."""
    
    def test_app_context_init_with_request_and_http_exception(self):
        """Test AppContext initialization when create_url_adapter raises HTTPException with request."""
        app = Flask(__name__)
        mock_request = Mock(spec=Request)
        mock_request.routing_exception = None
        
        # Create a specific HTTPException instance
        http_exception = HTTPException()
        http_exception.description = "Test routing error"
        
        # Mock create_url_adapter to raise HTTPException
        with patch.object(app, 'create_url_adapter', side_effect=http_exception):
            ctx = AppContext(app, request=mock_request)
            
            # Verify the context was created with expected attributes
            assert ctx.app is app
            assert ctx.g is not None
            assert ctx.url_adapter is None
            assert ctx._request is mock_request
            assert ctx._session is None
            assert ctx._flashes is None
            assert ctx._after_request_functions == []
            assert ctx._cv_token is None
            assert ctx._push_count == 0
            
            # Verify that routing_exception was set on the request
            assert mock_request.routing_exception is not None
            assert isinstance(mock_request.routing_exception, HTTPException)
            assert mock_request.routing_exception is http_exception
    
    def test_app_context_init_without_request_and_http_exception(self):
        """Test AppContext initialization when create_url_adapter raises HTTPException without request."""
        app = Flask(__name__)
        
        # Create a specific HTTPException instance
        http_exception = HTTPException()
        http_exception.description = "Test routing error"
        
        # Mock create_url_adapter to raise HTTPException
        with patch.object(app, 'create_url_adapter', side_effect=http_exception):
            ctx = AppContext(app, request=None)
            
            # Verify the context was created with expected attributes
            assert ctx.app is app
            assert ctx.g is not None
            assert ctx.url_adapter is None
            assert ctx._request is None
            assert ctx._session is None
            assert ctx._flashes is None
            assert ctx._after_request_functions == []
            assert ctx._cv_token is None
            assert ctx._push_count == 0
            
            # No request, so no routing_exception should be set
    
    def test_app_context_init_with_session(self):
        """Test AppContext initialization with session parameter."""
        app = Flask(__name__)
        mock_session = Mock()
        
        ctx = AppContext(app, session=mock_session)
        
        # Verify the context was created with expected attributes
        assert ctx.app is app
        assert ctx.g is not None
        assert ctx._session is mock_session
        assert ctx._request is None
        assert ctx._flashes is None
        assert ctx._after_request_functions == []
        assert ctx._cv_token is None
        assert ctx._push_count == 0
    
    def test_app_context_init_successful_url_adapter(self):
        """Test AppContext initialization when create_url_adapter succeeds."""
        app = Flask(__name__)
        mock_url_adapter = Mock()
        
        # Mock create_url_adapter to return a URL adapter
        with patch.object(app, 'create_url_adapter', return_value=mock_url_adapter):
            ctx = AppContext(app)
            
            # Verify the context was created with expected attributes
            assert ctx.app is app
            assert ctx.g is not None
            assert ctx.url_adapter is mock_url_adapter
            assert ctx._request is None
            assert ctx._session is None
            assert ctx._flashes is None
            assert ctx._after_request_functions == []
            assert ctx._cv_token is None
            assert ctx._push_count == 0
