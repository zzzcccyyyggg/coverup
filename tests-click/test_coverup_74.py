# file: src/click/src/click/core.py:1604-1620
# asked: {"lines": [1604, 1605, 1606, 1608, 1609, 1611, 1612, 1614, 1616, 1617, 1619, 1620], "branches": [[1608, 1609], [1608, 1619], [1611, 1612], [1611, 1614]]}
# gained: {"lines": [1604, 1605, 1606, 1608, 1609, 1611, 1612, 1614, 1616, 1617, 1619, 1620], "branches": [[1608, 1609], [1608, 1619], [1611, 1612], [1611, 1614]]}

import pytest
import click
from click.testing import CliRunner

def test_group_to_info_dict_with_commands():
    """Test Group.to_info_dict with multiple commands including None command."""
    @click.group()
    def cli():
        pass

    @cli.command()
    def cmd1():
        pass

    @cli.command()
    def cmd2():
        pass

    # Create a context
    ctx = click.Context(cli)
    
    # Mock list_commands to include a command that returns None
    original_list_commands = cli.list_commands
    def mock_list_commands(ctx):
        # Return command names including one that doesn't exist
        return ['cmd1', 'nonexistent', 'cmd2']
    
    # Mock get_command to return None for 'nonexistent'
    original_get_command = cli.get_command
    def mock_get_command(ctx, name):
        if name == 'nonexistent':
            return None
        return original_get_command(ctx, name)
    
    # Apply mocks
    cli.list_commands = mock_list_commands
    cli.get_command = mock_get_command
    
    try:
        # Call to_info_dict
        info_dict = cli.to_info_dict(ctx)
        
        # Verify the structure
        assert 'commands' in info_dict
        assert 'chain' in info_dict
        assert 'cmd1' in info_dict['commands']
        assert 'cmd2' in info_dict['commands']
        assert 'nonexistent' not in info_dict['commands']  # Should be skipped
        assert info_dict['chain'] == False
        
        # Verify command info structure
        cmd1_info = info_dict['commands']['cmd1']
        assert 'name' in cmd1_info
        assert cmd1_info['name'] == 'cmd1'
        
        cmd2_info = info_dict['commands']['cmd2']
        assert 'name' in cmd2_info
        assert cmd2_info['name'] == 'cmd2'
        
    finally:
        # Restore original methods
        cli.list_commands = original_list_commands
        cli.get_command = original_get_command

def test_group_to_info_dict_with_chain():
    """Test Group.to_info_dict with chain=True."""
    @click.group(chain=True)
    def cli():
        pass

    @cli.command()
    def cmd1():
        pass

    @cli.command()
    def cmd2():
        pass

    # Create a context
    ctx = click.Context(cli)
    
    # Call to_info_dict
    info_dict = cli.to_info_dict(ctx)
    
    # Verify chain is True
    assert info_dict['chain'] == True
    assert 'commands' in info_dict
    assert 'cmd1' in info_dict['commands']
    assert 'cmd2' in info_dict['commands']

def test_group_to_info_dict_empty_commands():
    """Test Group.to_info_dict with no commands."""
    @click.group()
    def cli():
        pass

    # Create a context
    ctx = click.Context(cli)
    
    # Call to_info_dict
    info_dict = cli.to_info_dict(ctx)
    
    # Verify empty commands dict
    assert 'commands' in info_dict
    assert info_dict['commands'] == {}
    assert 'chain' in info_dict
    assert info_dict['chain'] == False

def test_group_to_info_dict_subcommand_context():
    """Test Group.to_info_dict creates proper subcontexts for commands."""
    @click.group()
    def cli():
        pass

    @cli.command()
    def cmd1():
        pass

    # Create a context
    ctx = click.Context(cli)
    
    # Call to_info_dict
    info_dict = cli.to_info_dict(ctx)
    
    # Verify command info was created with subcontext
    assert 'commands' in info_dict
    assert 'cmd1' in info_dict['commands']
    cmd1_info = info_dict['commands']['cmd1']
    assert 'name' in cmd1_info
    assert cmd1_info['name'] == 'cmd1'
