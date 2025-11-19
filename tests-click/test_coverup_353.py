# file: src/click/src/click/core.py:746-750
# asked: {"lines": [746, 750], "branches": []}
# gained: {"lines": [746, 750], "branches": []}

import pytest
import click
from click.testing import CliRunner

class MockCommand:
    """A mock command class that implements get_help method and required attributes"""
    def __init__(self, help_text="Mock help text"):
        self.help_text = help_text
        self.allow_extra_args = False
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False
    
    def get_help(self, ctx):
        return self.help_text

def test_context_get_help():
    """Test that Context.get_help() calls command.get_help() and returns the result"""
    # Create a mock command with a specific help text
    mock_command = MockCommand("Test help text")
    
    # Create a context with the mock command
    ctx = click.Context(mock_command)
    
    # Call get_help and verify it returns the expected text
    result = ctx.get_help()
    
    # Assert that the result matches what the mock command returns
    assert result == "Test help text"

def test_context_get_help_with_different_help_text():
    """Test Context.get_help() with different help text to ensure it's properly delegated"""
    # Create a mock command with different help text
    mock_command = MockCommand("Different help text")
    
    # Create a context with the mock command
    ctx = click.Context(mock_command)
    
    # Call get_help and verify it returns the expected text
    result = ctx.get_help()
    
    # Assert that the result matches what the mock command returns
    assert result == "Different help text"

def test_context_get_help_integration():
    """Integration test using a real Click command to ensure get_help works correctly"""
    @click.command()
    def test_cmd():
        """Test command help"""
        pass
    
    # Create a context with the real command
    ctx = click.Context(test_cmd)
    
    # Call get_help and verify it returns a non-empty string
    result = ctx.get_help()
    
    # The help should contain the command name and description
    assert isinstance(result, str)
    assert len(result) > 0
    assert "test_cmd" in result or "Test command help" in result
