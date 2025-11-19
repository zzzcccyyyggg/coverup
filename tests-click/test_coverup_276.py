# file: src/click/src/click/core.py:760-763
# asked: {"lines": [760, 761, 763], "branches": []}
# gained: {"lines": [760, 761], "branches": []}

import pytest
import click
from click.core import Context
from typing import Callable, TypeVar

V = TypeVar('V')

def test_context_invoke_with_callable_overload():
    """Test the @t.overload for invoke with a generic callable."""
    
    # Create a simple command for the context
    @click.command()
    def dummy_command():
        pass
    
    # Create a context
    ctx = Context(dummy_command)
    
    # Define a callable that returns a specific type (string)
    def callback_func() -> str:
        return "test_result"
    
    # Test the invoke method with the callable
    result = ctx.invoke(callback_func)
    
    # Verify the result type and value
    assert result == "test_result"
    assert isinstance(result, str)

def test_context_invoke_with_callable_args_kwargs():
    """Test the @t.overload for invoke with a callable that takes args and kwargs."""
    
    @click.command()
    def dummy_command():
        pass
    
    ctx = Context(dummy_command)
    
    # Define a callable that takes arguments and returns a specific type
    def callback_with_args(a: int, b: str, *, c: bool = False) -> tuple[int, str, bool]:
        return a, b, c
    
    # Test the invoke method with positional and keyword arguments
    result = ctx.invoke(callback_with_args, 42, "hello", c=True)
    
    # Verify the result
    assert result == (42, "hello", True)
    assert isinstance(result, tuple)

def test_context_invoke_with_lambda():
    """Test the @t.overload for invoke with a lambda function."""
    
    @click.command()
    def dummy_command():
        pass
    
    ctx = Context(dummy_command)
    
    # Test with a lambda function
    result = ctx.invoke(lambda x, y: x + y, 10, 20)
    
    # Verify the result
    assert result == 30
    assert isinstance(result, int)
