# file: src/click/src/click/decorators.py:143-148
# asked: {"lines": [143, 144, 148], "branches": []}
# gained: {"lines": [143, 144], "branches": []}

import pytest
import typing as t
from click.decorators import command
from click.core import Command

class CustomCommand(Command):
    """A custom command class for testing."""
    pass

def test_command_overload_with_custom_class():
    """Test the command decorator overload with custom command class."""
    
    # Test the overload signature with custom command class
    @command("test_cmd", cls=CustomCommand, help="Test command")
    def test_func():
        """Test function for command decorator."""
        pass
    
    # Verify the result is an instance of the custom command class
    assert isinstance(test_func, CustomCommand)
    assert test_func.name == "test_cmd"
    assert test_func.help == "Test command"

def test_command_overload_with_custom_class_no_name():
    """Test the command decorator overload with custom command class but no name."""
    
    # Test the overload signature with custom command class but no name
    @command(cls=CustomCommand, help="Test command without name")
    def test_func_no_name():
        """Test function for command decorator without name."""
        pass
    
    # Verify the result is an instance of the custom command class
    assert isinstance(test_func_no_name, CustomCommand)
    # Click converts function names to kebab-case by default
    assert test_func_no_name.name == "test-func-no-name"
    assert test_func_no_name.help == "Test command without name"
