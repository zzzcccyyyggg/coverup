# file: src/click/src/click/core.py:1622-1630
# asked: {"lines": [1622, 1626, 1627, 1628, 1629, 1630], "branches": [[1627, 1628], [1627, 1629]]}
# gained: {"lines": [1622, 1626, 1627, 1628, 1629, 1630], "branches": [[1627, 1628], [1627, 1629]]}

import pytest
import click
from click.core import Group, Command, _check_nested_chain


class TestGroupAddCommand:
    """Test cases for Group.add_command method to achieve full coverage."""
    
    def test_add_command_with_name_provided(self):
        """Test add_command when name is explicitly provided."""
        group = Group('test_group')
        cmd = Command('cmd_name')
        
        group.add_command(cmd, name='custom_name')
        
        assert 'custom_name' in group.commands
        assert group.commands['custom_name'] is cmd
    
    def test_add_command_without_name_uses_cmd_name(self):
        """Test add_command when name is not provided, uses command's name."""
        group = Group('test_group')
        cmd = Command('cmd_name')
        
        group.add_command(cmd)
        
        assert 'cmd_name' in group.commands
        assert group.commands['cmd_name'] is cmd
    
    def test_add_command_raises_type_error_when_no_name(self):
        """Test add_command raises TypeError when command has no name and no name provided."""
        group = Group('test_group')
        cmd = Command(None)  # Command with no name
        
        with pytest.raises(TypeError, match="Command has no name."):
            group.add_command(cmd)
    
    def test_add_command_with_none_name_and_no_cmd_name(self):
        """Test add_command with explicit None name and command has no name."""
        group = Group('test_group')
        cmd = Command(None)  # Command with no name
        
        with pytest.raises(TypeError, match="Command has no name."):
            group.add_command(cmd, name=None)
    
    def test_add_command_with_chain_mode_and_group_command(self):
        """Test add_command calls _check_nested_chain when in chain mode with group command."""
        group = Group('test_group', chain=True)
        sub_group = Group('sub_group')
        
        with pytest.raises(RuntimeError, match="It is not possible to add the group 'sub_group' to another group 'test_group' that is in chain mode."):
            group.add_command(sub_group)
    
    def test_add_command_with_chain_mode_and_regular_command(self):
        """Test add_command works normally in chain mode with regular (non-group) command."""
        group = Group('test_group', chain=True)
        cmd = Command('regular_cmd')
        
        group.add_command(cmd)
        
        assert 'regular_cmd' in group.commands
        assert group.commands['regular_cmd'] is cmd
