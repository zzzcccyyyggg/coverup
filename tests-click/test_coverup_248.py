# file: src/click/src/click/decorators.py:152-158
# asked: {"lines": [152, 153, 154, 158], "branches": []}
# gained: {"lines": [152, 153, 154], "branches": []}

import pytest
import typing as t
from click.decorators import command
from click.core import Command

class CustomCommand(Command):
    """A custom command class for testing."""
    pass

def test_command_overload_with_custom_class():
    """Test the command decorator overload with custom command class."""
    
    # Test the overload where name is None and cls is provided
    @command(name=None, cls=CustomCommand)
    def test_func():
        """Test function for command decorator."""
        pass
    
    # Verify that the decorator returns a CustomCommand instance
    assert isinstance(test_func, CustomCommand)
    # Click converts function names to kebab-case by default
    assert test_func.name == "test-func"
