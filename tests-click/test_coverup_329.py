# file: src/click/src/click/core.py:740-744
# asked: {"lines": [740, 744], "branches": []}
# gained: {"lines": [740, 744], "branches": []}

import pytest
import click
from click.core import Context, Command

class MockCommand(Command):
    """A mock command for testing that tracks get_usage calls."""
    def __init__(self, name="test_command", usage_result="Usage: test_command [OPTIONS]"):
        super().__init__(name=name)
        self.usage_result = usage_result
        self.get_usage_called = False
        self.get_usage_context = None

    def get_usage(self, ctx):
        self.get_usage_called = True
        self.get_usage_context = ctx
        return self.usage_result

def test_context_get_usage():
    """Test that Context.get_usage() calls command.get_usage() with the context."""
    # Create a mock command with a specific usage result
    mock_command = MockCommand(usage_result="Usage: test_command [OPTIONS] ARG")
    
    # Create a context with the mock command
    ctx = Context(command=mock_command, info_name="test_command")
    
    # Call get_usage and verify it returns the expected result
    result = ctx.get_usage()
    
    # Assert that the command's get_usage method was called
    assert mock_command.get_usage_called, "Command.get_usage() was not called"
    
    # Assert that the context passed to command.get_usage() is the same context
    assert mock_command.get_usage_context is ctx, "Wrong context passed to command.get_usage()"
    
    # Assert that the result matches what the mock command returns
    assert result == "Usage: test_command [OPTIONS] ARG", f"Expected 'Usage: test_command [OPTIONS] ARG', got '{result}'"

def test_context_get_usage_with_different_command():
    """Test Context.get_usage() with a different command and usage string."""
    # Create another mock command with a different usage result
    mock_command = MockCommand(name="other_command", usage_result="Usage: other_command --verbose")
    
    # Create a context with this command
    ctx = Context(command=mock_command, info_name="other_command")
    
    # Call get_usage
    result = ctx.get_usage()
    
    # Verify the command's get_usage was called with the correct context
    assert mock_command.get_usage_called
    assert mock_command.get_usage_context is ctx
    
    # Verify the result matches
    assert result == "Usage: other_command --verbose"
