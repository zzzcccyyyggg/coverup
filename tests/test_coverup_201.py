# file: src/flask/src/flask/sansio/scaffold.py:701-706
# asked: {"lines": [701, 705, 706], "branches": []}
# gained: {"lines": [701, 705, 706], "branches": []}

import pytest
from flask import typing as ft
from flask.sansio.scaffold import _endpoint_from_view_func

def test_endpoint_from_view_func_with_valid_function():
    """Test that _endpoint_from_view_func returns the function name for a valid view function."""
    
    def sample_view():
        return "Hello World"
    
    result = _endpoint_from_view_func(sample_view)
    assert result == "sample_view"

def test_endpoint_from_view_func_with_none_raises_assertion():
    """Test that _endpoint_from_view_func raises AssertionError when view_func is None."""
    
    with pytest.raises(AssertionError, match="expected view func if endpoint is not provided."):
        _endpoint_from_view_func(None)

def test_endpoint_from_view_func_with_async_function():
    """Test that _endpoint_from_view_func works with async functions."""
    
    async def async_sample_view():
        return "Async Hello World"
    
    result = _endpoint_from_view_func(async_sample_view)
    assert result == "async_sample_view"
