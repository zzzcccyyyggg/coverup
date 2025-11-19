# file: src/click/src/click/core.py:1635-1638
# asked: {"lines": [1635, 1636, 1638], "branches": []}
# gained: {"lines": [1635, 1636], "branches": []}

import pytest
import click
from click.testing import CliRunner

def test_group_command_overload_decorator():
    """Test that the @t.overload decorator for Group.command is executed."""
    
    # Create a group
    @click.group()
    def cli():
        pass
    
    # The @t.overload decorator should be executed when the class is defined
    # We can verify this by checking that the method exists and has the expected signature
    assert hasattr(cli, 'command')
    assert callable(cli.command)
    
    # Test that we can use the command decorator with a function
    @cli.command()
    def test_cmd():
        """Test command."""
        click.echo("success")
    
    # Verify the command was added (command names use the function name without underscores)
    assert 'test' in cli.commands
    
    # Test invocation
    runner = CliRunner()
    result = runner.invoke(cli, ['test'])
    assert result.exit_code == 0
    assert "success" in result.output

def test_group_command_overload_with_arguments():
    """Test the overloaded command decorator with arguments."""
    
    @click.group()
    def cli():
        pass
    
    # Test command decorator with name argument
    @cli.command(name='custom-name')
    def test_cmd():
        """Test command with custom name."""
        click.echo("custom success")
    
    # Verify the command was added with custom name
    assert 'custom-name' in cli.commands
    assert 'test' not in cli.commands
    
    # Test invocation
    runner = CliRunner()
    result = runner.invoke(cli, ['custom-name'])
    assert result.exit_code == 0
    assert "custom success" in result.output

def test_group_command_overload_direct_function():
    """Test the overloaded command decorator when applied directly to a function."""
    
    @click.group()
    def cli():
        pass
    
    def direct_cmd():
        """Direct command function."""
        click.echo("direct success")
    
    # Apply command decorator directly to function
    decorated_cmd = cli.command()(direct_cmd)
    
    # Verify the command was added and decorator returned the command
    assert 'direct' in cli.commands
    assert decorated_cmd.name == 'direct'
    
    # Test invocation
    runner = CliRunner()
    result = runner.invoke(cli, ['direct'])
    assert result.exit_code == 0
    assert "direct success" in result.output
