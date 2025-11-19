# file: src/click/src/click/core.py:1778-1782
# asked: {"lines": [1778, 1782], "branches": []}
# gained: {"lines": [1778, 1782], "branches": []}

import pytest
import click
from click.core import Group, Context, Command

class TestGroupGetCommand:
    """Test cases for Group.get_command method to achieve full coverage."""
    
    def test_get_command_existing_command(self):
        """Test get_command returns existing command."""
        # Create a group with commands
        group = Group('test_group')
        cmd1 = Command('cmd1')
        cmd2 = Command('cmd2')
        group.commands = {'cmd1': cmd1, 'cmd2': cmd2}
        
        # Create a context
        ctx = Context(group)
        
        # Test getting existing command
        result = group.get_command(ctx, 'cmd1')
        assert result is cmd1
        
        # Test getting another existing command
        result = group.get_command(ctx, 'cmd2')
        assert result is cmd2
    
    def test_get_command_nonexistent_command(self):
        """Test get_command returns None for non-existent command."""
        # Create a group with some commands
        group = Group('test_group')
        cmd1 = Command('cmd1')
        group.commands = {'cmd1': cmd1}
        
        # Create a context
        ctx = Context(group)
        
        # Test getting non-existent command
        result = group.get_command(ctx, 'nonexistent')
        assert result is None
    
    def test_get_command_empty_commands_dict(self):
        """Test get_command with empty commands dictionary."""
        # Create a group with no commands
        group = Group('test_group')
        group.commands = {}
        
        # Create a context
        ctx = Context(group)
        
        # Test getting any command should return None
        result = group.get_command(ctx, 'any_command')
        assert result is None
    
    def test_get_command_with_no_commands_initialized(self):
        """Test get_command when group is initialized without commands."""
        # Create a group without specifying commands (defaults to empty dict)
        group = Group('test_group')
        
        # Create a context
        ctx = Context(group)
        
        # Test getting command should return None
        result = group.get_command(ctx, 'any_command')
        assert result is None
