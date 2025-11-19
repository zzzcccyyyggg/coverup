# file: src/flask/src/flask/helpers.py:62-135
# asked: {"lines": [], "branches": [[127, 0]]}
# gained: {"lines": [], "branches": [[127, 0]]}

import pytest
import typing as t
from flask.helpers import stream_with_context
from flask.globals import _cv_app
from flask import Flask


class TestStreamWithContext:
    def test_stream_with_context_with_closeable_generator(self):
        """Test that stream_with_context properly closes generators with close() method."""
        app = Flask(__name__)
        
        close_called = []
        
        class CloseableGenerator:
            def __iter__(self):
                return self
            
            def __next__(self):
                raise StopIteration
            
            def close(self):
                close_called.append(True)
        
        gen = CloseableGenerator()
        
        with app.test_request_context():
            wrapped = stream_with_context(gen)
            # Consume the generator to trigger the finally block
            list(wrapped)
        
        assert close_called == [True]

    def test_stream_with_context_without_closeable_generator(self):
        """Test that stream_with_context works with generators without close() method."""
        app = Flask(__name__)
        
        def simple_generator():
            yield "Hello"
            yield "World"
        
        gen = simple_generator()
        
        with app.test_request_context():
            wrapped = stream_with_context(gen)
            result = list(wrapped)
        
        assert result == ["Hello", "World"]
        # Should not raise any errors even though gen doesn't have close()

    def test_stream_with_context_decorator_with_closeable_generator(self):
        """Test the decorator form with a closeable generator."""
        app = Flask(__name__)
        
        close_called = []
        
        class CloseableGenerator:
            def __iter__(self):
                return self
            
            def __next__(self):
                raise StopIteration
            
            def close(self):
                close_called.append(True)
        
        gen = CloseableGenerator()
        
        @stream_with_context
        def generate():
            return gen
        
        with app.test_request_context():
            wrapped = generate()
            # Consume the generator to trigger the finally block
            list(wrapped)
        
        assert close_called == [True]

    def test_stream_with_context_with_wsgi_iterator_close(self):
        """Test that stream_with_context calls close() on WSGI iterators that have it."""
        app = Flask(__name__)
        
        close_called = []
        
        class WSGIIterator:
            def __init__(self):
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
                close_called.append(True)
        
        gen = WSGIIterator()
        
        with app.test_request_context():
            wrapped = stream_with_context(gen)
            result = list(wrapped)
        
        assert result == ["Hello", "World"]
        assert close_called == [True]

    def test_stream_with_context_with_wsgi_iterator_no_close(self):
        """Test that stream_with_context works with WSGI iterators without close() method."""
        app = Flask(__name__)
        
        class WSGIIteratorNoClose:
            def __init__(self):
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
        
        gen = WSGIIteratorNoClose()
        
        with app.test_request_context():
            wrapped = stream_with_context(gen)
            result = list(wrapped)
        
        assert result == ["Hello", "World"]
        # Should not raise any errors even though gen doesn't have close()
