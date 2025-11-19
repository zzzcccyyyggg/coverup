# file: src/flask/src/flask/ctx.py:409-430
# asked: {"lines": [409, 421, 423, 424, 426, 427, 429, 430], "branches": [[423, 424], [423, 426], [429, 0], [429, 430]]}
# gained: {"lines": [409, 421, 423, 424, 426, 427, 429, 430], "branches": [[423, 424], [423, 426], [429, 0], [429, 430]]}

import pytest
from flask import Flask
from flask.ctx import AppContext
from werkzeug.routing import MapAdapter
from werkzeug.exceptions import NotFound
from unittest.mock import Mock, patch
from werkzeug.datastructures import Headers


class TestAppContextPush:
    """Test cases for AppContext.push method to achieve full coverage."""
    
    def test_push_multiple_times_returns_early(self):
        """Test that push returns early when _cv_token is already set."""
        app = Flask(__name__)
        ctx = AppContext(app)
        
        # Set up initial state to simulate already pushed context
        ctx._cv_token = Mock()
        initial_push_count = ctx._push_count
        
        # Call push - should return early due to existing _cv_token
        ctx.push()
        
        # Verify push count was incremented but no other changes occurred
        assert ctx._push_count == initial_push_count + 1
        # _cv_token should remain unchanged
        assert ctx._cv_token is not None
        
    def test_push_with_request_and_url_adapter_calls_match_request(self, monkeypatch):
        """Test that push calls match_request when both _request and url_adapter are set."""
        app = Flask(__name__)
        
        # Create a proper mock request with required attributes
        mock_request = Mock()
        mock_request.environ = {
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'localhost:5000',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000'
        }
        mock_request.trusted_hosts = None
        
        # Create AppContext without request first, then manually set attributes
        ctx = AppContext(app)
        ctx._request = mock_request
        ctx.url_adapter = Mock()
        
        # Mock the contextvars and signals
        mock_token = Mock()
        mock_cv_app = Mock()
        mock_cv_app.set.return_value = mock_token
        
        # Track if match_request was called
        match_request_called = False
        
        def mock_match_request():
            nonlocal match_request_called
            match_request_called = True
        
        # Apply monkeypatches
        monkeypatch.setattr('flask.ctx._cv_app', mock_cv_app)
        monkeypatch.setattr('flask.ctx.appcontext_pushed.send', Mock())
        monkeypatch.setattr(ctx, 'match_request', mock_match_request)
        
        # Call push
        ctx.push()
        
        # Verify the expected behavior
        assert ctx._push_count == 1
        assert ctx._cv_token == mock_token
        mock_cv_app.set.assert_called_once_with(ctx)
        assert match_request_called is True
        
    def test_push_with_request_but_no_url_adapter_skips_match_request(self, monkeypatch):
        """Test that push does not call match_request when url_adapter is None."""
        app = Flask(__name__)
        
        # Create a proper mock request with required attributes
        mock_request = Mock()
        mock_request.environ = {
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'localhost:5000',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000'
        }
        mock_request.trusted_hosts = None
        
        # Create AppContext without request first, then manually set attributes
        ctx = AppContext(app)
        ctx._request = mock_request
        ctx.url_adapter = None  # Explicitly set to None
        
        # Mock the contextvars and signals
        mock_token = Mock()
        mock_cv_app = Mock()
        mock_cv_app.set.return_value = mock_token
        
        # Track if match_request was called
        match_request_called = False
        
        def mock_match_request():
            nonlocal match_request_called
            match_request_called = True
        
        # Apply monkeypatches
        monkeypatch.setattr('flask.ctx._cv_app', mock_cv_app)
        monkeypatch.setattr('flask.ctx.appcontext_pushed.send', Mock())
        monkeypatch.setattr(ctx, 'match_request', mock_match_request)
        
        # Call push
        ctx.push()
        
        # Verify the expected behavior
        assert ctx._push_count == 1
        assert ctx._cv_token == mock_token
        mock_cv_app.set.assert_called_once_with(ctx)
        assert match_request_called is False  # Should not be called
        
    def test_push_with_url_adapter_but_no_request_skips_match_request(self, monkeypatch):
        """Test that push does not call match_request when _request is None."""
        app = Flask(__name__)
        
        # Create URL adapter but no request
        mock_url_adapter = Mock()
        
        ctx = AppContext(app)  # No request parameter
        ctx.url_adapter = mock_url_adapter
        
        # Mock the contextvars and signals
        mock_token = Mock()
        mock_cv_app = Mock()
        mock_cv_app.set.return_value = mock_token
        
        # Track if match_request was called
        match_request_called = False
        
        def mock_match_request():
            nonlocal match_request_called
            match_request_called = True
        
        # Apply monkeypatches
        monkeypatch.setattr('flask.ctx._cv_app', mock_cv_app)
        monkeypatch.setattr('flask.ctx.appcontext_pushed.send', Mock())
        monkeypatch.setattr(ctx, 'match_request', mock_match_request)
        
        # Call push
        ctx.push()
        
        # Verify the expected behavior
        assert ctx._push_count == 1
        assert ctx._cv_token == mock_token
        mock_cv_app.set.assert_called_once_with(ctx)
        assert match_request_called is False  # Should not be called
