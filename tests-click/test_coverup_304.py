# file: src/click/src/click/decorators.py:137-138
# asked: {"lines": [137, 138], "branches": []}
# gained: {"lines": [137, 138], "branches": []}

import pytest
import typing as t
from click.decorators import command
from click.core import Command

def test_command_overload_with_callable() -> None:
    """Test the @t.overload for command with callable parameter."""
    
    def sample_func() -> None:
        pass
    
    # This should trigger the overload where name is a callable
    result = command(sample_func)
    
    # Verify the result is a Command instance
    assert isinstance(result, Command)
    assert result.callback is sample_func

def test_command_overload_with_callable_verify_type_hint() -> None:
    """Test that the type hint for the overload is properly checked."""
    
    def another_func() -> str:
        return "test"
    
    # This should use the overload: def command(name: _AnyCallable) -> Command
    cmd = command(another_func)
    
    assert isinstance(cmd, Command)
    assert cmd.callback is another_func
