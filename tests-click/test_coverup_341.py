# file: src/click/src/click/core.py:1784-1786
# asked: {"lines": [1784, 1786], "branches": []}
# gained: {"lines": [1784, 1786], "branches": []}

import pytest
import click
from click.core import Context, Group, Command

class TestGroupListCommands:
    def test_list_commands_empty(self):
        """Test list_commands returns empty list when no commands are present."""
        group = Group('test_group')
        ctx = Context(group)
        
        result = group.list_commands(ctx)
        
        assert result == []
    
    def test_list_commands_single_command(self):
        """Test list_commands returns sorted list with single command."""
        group = Group('test_group')
        cmd = Command('cmd1')
        group.add_command(cmd)
        ctx = Context(group)
        
        result = group.list_commands(ctx)
        
        assert result == ['cmd1']
    
    def test_list_commands_multiple_commands_unsorted(self):
        """Test list_commands returns sorted list when commands are added in unsorted order."""
        group = Group('test_group')
        cmd1 = Command('z_command')
        cmd2 = Command('a_command')
        cmd3 = Command('m_command')
        group.add_command(cmd1)
        group.add_command(cmd2)
        group.add_command(cmd3)
        ctx = Context(group)
        
        result = group.list_commands(ctx)
        
        assert result == ['a_command', 'm_command', 'z_command']
    
    def test_list_commands_with_commands_dict(self):
        """Test list_commands works when commands are provided as dict during initialization."""
        cmd1 = Command('beta')
        cmd2 = Command('alpha')
        cmd3 = Command('gamma')
        commands = {'beta': cmd1, 'alpha': cmd2, 'gamma': cmd3}
        group = Group('test_group', commands=commands)
        ctx = Context(group)
        
        result = group.list_commands(ctx)
        
        assert result == ['alpha', 'beta', 'gamma']
