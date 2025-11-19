# file: src/flask/src/flask/helpers.py:62-135
# asked: {"lines": [62, 103, 104, 105, 107, 108, 109, 111, 113, 114, 115, 116, 120, 121, 123, 124, 127, 128, 133, 134, 135], "branches": [[114, 115], [114, 120], [127, 0], [127, 128]]}
# gained: {"lines": [62, 103, 104, 105, 107, 111, 113, 114, 115, 116, 120, 121, 123, 124, 127, 128, 133, 134, 135], "branches": [[114, 115], [114, 120], [127, 128]]}

import pytest
import typing as t
from flask.helpers import stream_with_context
from flask.globals import _cv_app
from unittest.mock import Mock, patch
import contextvars


class TestStreamWithContext:
    def test_stream_with_context_as_decorator_with_function(self):
        """Test stream_with_context as decorator with a generator function."""
        @stream_with_context
        def generate():
            yield "Hello"
            yield "World"
        
        # The decorator should return a callable
        assert callable(generate)
        
        # The decorator should wrap the function but not execute it yet
        assert generate.__name__ == "generate"
    
    def test_stream_with_context_as_wrapper_with_generator_no_request_context(self):
        """Test stream_with_context as wrapper with generator when no request context is active."""
        def generate():
            yield "Hello"
            yield "World"
        
        gen = generate()
        
        # Should raise RuntimeError when no request context is active
        with pytest.raises(RuntimeError, match="'stream_with_context' can only be used when a request context is active"):
            stream_with_context(gen)
    
    def test_stream_with_context_as_wrapper_with_generator_with_request_context(self):
        """Test stream_with_context as wrapper with generator when request context is active."""
        def generate():
            yield "Hello"
            yield "World"
        
        gen = generate()
        
        # Mock the request context by setting a value in the context var
        mock_ctx = Mock()
        mock_ctx.__enter__ = Mock()
        mock_ctx.__exit__ = Mock(return_value=None)
        
        # Use contextvars to set a mock context
        token = _cv_app.set(mock_ctx)
        try:
            # Call stream_with_context
            result = stream_with_context(gen)
            
            # Should return an iterator
            assert hasattr(result, '__iter__')
            
            # Consume the iterator to ensure cleanup happens
            items = list(result)
            assert items == ["Hello", "World"]
            
            # Verify context was entered and exited
            mock_ctx.__enter__.assert_called_once()
            mock_ctx.__exit__.assert_called_once()
        finally:
            _cv_app.reset(token)
    
    def test_stream_with_context_with_closeable_generator(self):
        """Test stream_with_context with a generator that has a close method."""
        class CloseableGenerator:
            def __init__(self):
                self.closed = False
                self.items = ["Hello", "World"]
                self.index = 0
            
            def __iter__(self):
                return self
            
            def __next__(self):
                if self.index >= len(self.items):
                    raise StopIteration
                item = self.items[self.index]
                self.index += 1
                return item
            
            def close(self):
                self.closed = True
        
        gen = CloseableGenerator()
        
        # Mock the request context
        mock_ctx = Mock()
        mock_ctx.__enter__ = Mock()
        mock_ctx.__exit__ = Mock(return_value=None)
        
        # Use contextvars to set a mock context
        token = _cv_app.set(mock_ctx)
        try:
            # Call stream_with_context
            result = stream_with_context(gen)
            
            # Consume the iterator
            items = list(result)
            assert items == ["Hello", "World"]
            
            # Verify close was called
            assert gen.closed is True
            
            # Verify context was entered and exited
            mock_ctx.__enter__.assert_called_once()
            mock_ctx.__exit__.assert_called_once()
        finally:
            _cv_app.reset(token)
    
    def test_stream_with_context_with_non_closeable_generator(self):
        """Test stream_with_context with a generator that doesn't have a close method."""
        def generate():
            yield "Hello"
            yield "World"
        
        gen = generate()
        
        # Mock the request context
        mock_ctx = Mock()
        mock_ctx.__enter__ = Mock()
        mock_ctx.__exit__ = Mock(return_value=None)
        
        # Use contextvars to set a mock context
        token = _cv_app.set(mock_ctx)
        try:
            # Call stream_with_context
            result = stream_with_context(gen)
            
            # Consume the iterator - should not raise any errors
            items = list(result)
            assert items == ["Hello", "World"]
            
            # Verify context was entered and exited
            mock_ctx.__enter__.assert_called_once()
            mock_ctx.__exit__.assert_called_once()
        finally:
            _cv_app.reset(token)
