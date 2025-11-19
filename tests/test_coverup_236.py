# file: src/flask/src/flask/helpers.py:56-59
# asked: {"lines": [56, 57, 59], "branches": []}
# gained: {"lines": [56, 57], "branches": []}

import pytest
import typing as t
from flask import Flask
from flask.helpers import stream_with_context


def test_stream_with_context_overload_with_callable():
    """Test the @t.overload decorator for stream_with_context with callable parameter."""
    
    app = Flask(__name__)
    
    with app.test_request_context():
        # Create a simple generator function that matches the overload signature
        def test_generator() -> t.Iterator[str]:
            yield "test"
            yield "data"
        
        # The overload should accept this callable and return a callable
        decorated_func = stream_with_context(test_generator)
        
        # Verify the decorated function is callable
        assert callable(decorated_func)
        
        # Call the decorated function to get an iterator
        result = decorated_func()
        
        # Verify it returns an iterator
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')
        
        # Consume the iterator to verify it works
        items = list(result)
        assert items == ["test", "data"]


def test_stream_with_context_overload_with_iterator():
    """Test the @t.overload decorator for stream_with_context with iterator parameter."""
    
    app = Flask(__name__)
    
    with app.test_request_context():
        # Create a simple iterator that matches the overload signature
        def test_iterator() -> t.Iterator[str]:
            yield "iterator"
            yield "test"
        
        iterator = test_iterator()
        
        # The overload should accept the iterator directly and return an iterator
        result = stream_with_context(iterator)
        
        # Verify it returns an iterator
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')
        
        # Consume the iterator to verify it works
        items = list(result)
        assert items == ["iterator", "test"]
