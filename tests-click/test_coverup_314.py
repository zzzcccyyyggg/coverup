# file: src/click/src/click/core.py:990-991
# asked: {"lines": [990, 991], "branches": []}
# gained: {"lines": [990, 991], "branches": []}

import pytest
import click


def test_command_repr():
    """Test that Command.__repr__ returns the expected string format."""
    # Create a command with a name
    cmd = click.Command(name="test_command")
    
    # Test the repr method
    result = repr(cmd)
    
    # Verify the format matches expected pattern
    assert result == "<Command test_command>"
    
    # Test with a different command name
    cmd2 = click.Command(name="another_command")
    result2 = repr(cmd2)
    assert result2 == "<Command another_command>"
