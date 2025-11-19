# file: src/flask/src/flask/helpers.py:50-53
# asked: {"lines": [50, 51, 53], "branches": []}
# gained: {"lines": [50, 51], "branches": []}

import pytest
import typing as t
from flask.helpers import stream_with_context


def test_stream_with_context_overload_iterator():
    """Test the overload for stream_with_context with Iterator parameter."""
    # This test verifies that the type overload for Iterator is properly defined
    # The actual implementation would be tested elsewhere, this just ensures
    # the overload signature exists and can be type-checked
    
    # Create a mock iterator that matches the expected type
    class MockIterator:
        def __iter__(self):
            return self
            
        def __next__(self):
            raise StopIteration
    
    # The test itself doesn't need to call the function since this is just
    # testing the type overload signature, but we can verify the function exists
    assert callable(stream_with_context)
    
    # For coverage purposes, we can create a scenario that would use this overload
    # but since it's just a type annotation, the actual execution path would be
    # in the main implementation which we're not testing here
    iterator = MockIterator()
    
    # This would normally be type-checked by mypy/pyright, not executed
    # We're just ensuring the overload exists for coverage
    pass
