# file: src/click/src/click/decorators.py:162-165
# asked: {"lines": [162, 163, 164, 165], "branches": []}
# gained: {"lines": [162, 163, 164], "branches": []}

import pytest
import click
from click.decorators import command
from click.core import Command

def test_command_overload_with_name_and_no_cls():
    """Test the @t.overload for command with name and cls=None."""
    
    @command(name="test_command", cls=None)
    def test_func():
        """Test function for command decorator."""
        return "test"
    
    # Verify the result is a Command instance
    assert isinstance(test_func, Command)
    assert test_func.name == "test_command"
    assert test_func.callback is not None

def test_command_overload_with_name_str_and_no_cls():
    """Test the @t.overload for command with string name and cls=None."""
    
    @command(name="another_command", cls=None)
    def another_func():
        """Another test function."""
        return "another"
    
    # Verify the result is a Command instance
    assert isinstance(another_func, Command)
    assert another_func.name == "another_command"
    assert another_func.callback is not None

def test_command_overload_with_none_name_and_no_cls():
    """Test the @t.overload for command with None name and cls=None."""
    
    @command(name=None, cls=None)
    def none_name_func():
        """Function with None name."""
        return "none_name"
    
    # Verify the result is a Command instance
    assert isinstance(none_name_func, Command)
    # Click converts function names to kebab-case by default
    assert none_name_func.name == "none-name-func"
    assert none_name_func.callback is not None
