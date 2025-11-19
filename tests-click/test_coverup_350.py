# file: src/click/src/click/core.py:765-766
# asked: {"lines": [765, 766], "branches": []}
# gained: {"lines": [765, 766], "branches": []}

import pytest
import click
from click.core import Context, Command

def test_context_invoke_command_overload():
    """Test that the Command overload signature for Context.invoke is covered."""
    
    def test_callback():
        return "command_result"
    
    # Create a command with a callback
    cmd = Command("test", callback=test_callback)
    
    # Create a context
    ctx = Context(cmd)
    
    # Invoke the command using the Command overload signature
    result = ctx.invoke(cmd)
    
    # Verify the command was invoked and returned expected result
    assert result == "command_result"

def test_context_invoke_callable_overload():
    """Test that the Callable overload signature for Context.invoke is covered."""
    
    def test_callback(*args, **kwargs):
        return "callback_result"
    
    # Create a context with a dummy command
    cmd = Command("dummy")
    ctx = Context(cmd)
    
    # Invoke the callback using the Callable overload signature
    result = ctx.invoke(test_callback)
    
    # Verify the callback was invoked and returned expected result
    assert result == "callback_result"

def test_context_invoke_with_args_and_kwargs():
    """Test Context.invoke with additional arguments and keyword arguments."""
    
    def test_callback(arg1, arg2, kwarg1=None, kwarg2=None):
        return f"{arg1}_{arg2}_{kwarg1}_{kwarg2}"
    
    cmd = Command("dummy")
    ctx = Context(cmd)
    
    # Invoke with args and kwargs
    result = ctx.invoke(test_callback, "a", "b", kwarg1="c", kwarg2="d")
    
    assert result == "a_b_c_d"
