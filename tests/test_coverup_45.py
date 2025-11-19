# file: src/flask/src/flask/app.py:806-857
# asked: {"lines": [806, 834, 835, 836, 838, 839, 841, 844, 845, 847, 849, 851, 852, 854, 855, 857], "branches": [[838, 839], [838, 841], [841, 844], [841, 849], [844, 845], [844, 847], [854, 855], [854, 857]]}
# gained: {"lines": [806, 834, 835, 836, 838, 839, 841, 844, 845, 847, 849, 851, 852, 854, 855, 857], "branches": [[838, 839], [838, 841], [841, 844], [841, 849], [844, 845], [844, 847], [854, 855], [854, 857]]}

import pytest
from werkzeug.exceptions import InternalServerError
from flask import Flask, request
import sys
import asyncio

class TestFlaskHandleException:
    def test_handle_exception_propagate_true_with_same_exception(self):
        """Test handle_exception when PROPAGATE_EXCEPTIONS is True and exc_info[1] is e"""
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = True
        
        with app.test_request_context():
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                with pytest.raises(ValueError, match="Test exception"):
                    app.handle_exception(e)

    def test_handle_exception_propagate_true_with_different_exception(self):
        """Test handle_exception when PROPAGATE_EXCEPTIONS is True and exc_info[1] is not e"""
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = True
        
        with app.test_request_context():
            try:
                raise ValueError("Original exception")
            except ValueError:
                pass
            
            new_exception = RuntimeError("New exception")
            with pytest.raises(RuntimeError, match="New exception"):
                app.handle_exception(new_exception)

    def test_handle_exception_propagate_none_testing_true(self):
        """Test handle_exception when PROPAGATE_EXCEPTIONS is None and testing is True"""
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = None
        app.testing = True
        
        with app.test_request_context():
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                with pytest.raises(ValueError, match="Test exception"):
                    app.handle_exception(e)

    def test_handle_exception_propagate_none_debug_true(self):
        """Test handle_exception when PROPAGATE_EXCEPTIONS is None and debug is True"""
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = None
        app.debug = True
        
        with app.test_request_context():
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                with pytest.raises(ValueError, match="Test exception"):
                    app.handle_exception(e)

    def test_handle_exception_propagate_false_no_handler(self, monkeypatch):
        """Test handle_exception when PROPAGATE_EXCEPTIONS is False and no error handler"""
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = False
        
        # Mock log_exception to avoid actual logging
        mock_log_called = False
        def mock_log_exception(exc_info):
            nonlocal mock_log_called
            mock_log_called = True
        monkeypatch.setattr(app, 'log_exception', mock_log_exception)
        
        # Mock finalize_request to return a simple response
        def mock_finalize_request(rv, from_error_handler=False):
            return "finalized_response"
        monkeypatch.setattr(app, 'finalize_request', mock_finalize_request)
        
        with app.test_request_context():
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                result = app.handle_exception(e)
        
        assert mock_log_called
        assert result == "finalized_response"

    def test_handle_exception_propagate_false_with_handler(self, monkeypatch):
        """Test handle_exception when PROPAGATE_EXCEPTIONS is False and error handler exists"""
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = False
        
        # Mock log_exception to avoid actual logging
        mock_log_called = False
        def mock_log_exception(exc_info):
            nonlocal mock_log_called
            mock_log_called = True
        monkeypatch.setattr(app, 'log_exception', mock_log_exception)
        
        # Create a mock error handler
        handler_called = False
        def error_handler(e):
            nonlocal handler_called
            handler_called = True
            assert isinstance(e, InternalServerError)
            assert e.original_exception.args[0] == "Test exception"
            return "handled_response"
        
        # Mock _find_error_handler to return our handler
        def mock_find_error_handler(error, blueprints):
            return error_handler
        monkeypatch.setattr(app, '_find_error_handler', mock_find_error_handler)
        
        # Mock finalize_request to return a simple response
        def mock_finalize_request(rv, from_error_handler=False):
            return f"finalized_{rv}"
        monkeypatch.setattr(app, 'finalize_request', mock_finalize_request)
        
        with app.test_request_context():
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                result = app.handle_exception(e)
        
        assert mock_log_called
        assert handler_called
        assert result == "finalized_handled_response"

    def test_handle_exception_propagate_false_with_async_handler(self, monkeypatch):
        """Test handle_exception when PROPAGATE_EXCEPTIONS is False and async error handler exists"""
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = False
        
        # Mock log_exception to avoid actual logging
        mock_log_called = False
        def mock_log_exception(exc_info):
            nonlocal mock_log_called
            mock_log_called = True
        monkeypatch.setattr(app, 'log_exception', mock_log_exception)
        
        # Create a mock async handler that actually executes
        async_handler_called = False
        async def async_error_handler(e):
            nonlocal async_handler_called
            async_handler_called = True
            assert isinstance(e, InternalServerError)
            assert e.original_exception.args[0] == "Test exception"
            return "async_handled_response"
        
        # Mock _find_error_handler to return our async handler
        def mock_find_error_handler(error, blueprints):
            return async_error_handler
        monkeypatch.setattr(app, '_find_error_handler', mock_find_error_handler)
        
        # Mock async_to_sync to properly execute the async function
        def mock_async_to_sync(func):
            def sync_wrapper(*args, **kwargs):
                # Run the async function to completion
                return asyncio.run(func(*args, **kwargs))
            return sync_wrapper
        monkeypatch.setattr(app, 'async_to_sync', mock_async_to_sync)
        
        # Mock finalize_request to return a simple response
        def mock_finalize_request(rv, from_error_handler=False):
            return f"finalized_{rv}"
        monkeypatch.setattr(app, 'finalize_request', mock_finalize_request)
        
        with app.test_request_context():
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                result = app.handle_exception(e)
        
        assert mock_log_called
        assert async_handler_called
        assert result == "finalized_async_handled_response"
