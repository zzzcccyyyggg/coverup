# file: src/click/src/click/core.py:1681-1682
# asked: {"lines": [1681, 1682], "branches": []}
# gained: {"lines": [1681, 1682], "branches": []}

import pytest
import click
from click.testing import CliRunner

def test_group_decorator_overload():
    """Test the @t.overload decorator for Group.group method with __func parameter."""
    
    @click.group()
    def cli():
        pass
    
    # Test that the group decorator can be used with a function
    @cli.group()
    def subcommand():
        pass
    
    # Verify the subcommand was added to the group
    assert 'subcommand' in cli.commands
    assert isinstance(cli.commands['subcommand'], click.Group)
    
    # Test that the decorated function returns a Group instance
    runner = CliRunner()
    result = runner.invoke(cli, ['subcommand', '--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output
