# file: src/click/src/click/utils.py:36-46
# asked: {"lines": [36, 39, 40, 41, 42, 43, 44, 46], "branches": []}
# gained: {"lines": [36, 39, 40, 41, 42, 43, 44, 46], "branches": []}

import pytest
import typing as t
from click.utils import safecall


def test_safecall_successful_execution():
    """Test that safecall returns the result when no exception occurs."""
    
    def test_func(x: int, y: int) -> int:
        return x + y
    
    wrapped_func = safecall(test_func)
    result = wrapped_func(2, 3)
    
    assert result == 5
    assert wrapped_func.__name__ == 'test_func'


def test_safecall_exception_swallowed():
    """Test that safecall returns None when an exception occurs."""
    
    def test_func_raises(x: int, y: int) -> int:
        raise ValueError("Test exception")
    
    wrapped_func = safecall(test_func_raises)
    result = wrapped_func(2, 3)
    
    assert result is None
    assert wrapped_func.__name__ == 'test_func_raises'


def test_safecall_with_keyword_arguments():
    """Test that safecall works with keyword arguments."""
    
    def test_func_kwargs(a: int, b: int = 0) -> int:
        return a + b
    
    wrapped_func = safecall(test_func_kwargs)
    result = wrapped_func(a=5, b=3)
    
    assert result == 8
    assert wrapped_func.__name__ == 'test_func_kwargs'


def test_safecall_with_exception_and_kwargs():
    """Test that safecall returns None when exception occurs with keyword arguments."""
    
    def test_func_kwargs_raises(a: int, b: int = 0) -> int:
        raise RuntimeError("Test exception with kwargs")
    
    wrapped_func = safecall(test_func_kwargs_raises)
    result = wrapped_func(a=5, b=3)
    
    assert result is None
    assert wrapped_func.__name__ == 'test_func_kwargs_raises'
