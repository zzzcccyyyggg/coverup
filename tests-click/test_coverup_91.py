# file: src/click/src/click/decorators.py:380-401
# asked: {"lines": [380, 389, 390, 391, 393, 394, 396, 397, 398, 399, 400, 401], "branches": [[390, 0], [390, 391], [393, 394], [393, 396]]}
# gained: {"lines": [380, 389, 390, 391, 393, 394, 396, 397, 398, 399, 400, 401], "branches": [[390, 0], [390, 391], [393, 394], [393, 396]]}

import pytest
import click
from click.testing import CliRunner
from click.exceptions import Abort


def test_confirmation_option_callback_aborts_when_false():
    """Test that the callback aborts when value is False."""
    from click.decorators import confirmation_option
    
    @click.command()
    @confirmation_option()
    def test_cmd():
        click.echo("Command executed")
    
    # Get the callback from the option
    option = test_cmd.params[0]
    callback = option.callback
    
    # Test when confirmation is not provided (value=False)
    with pytest.raises(Abort):
        ctx = click.Context(test_cmd)
        callback(ctx, option, False)


def test_confirmation_option_callback_continues_when_true():
    """Test that the callback continues when value is True."""
    from click.decorators import confirmation_option
    
    @click.command()
    @confirmation_option()
    def test_cmd():
        click.echo("Command executed")
    
    # Get the callback from the option
    option = test_cmd.params[0]
    callback = option.callback
    
    # Test when confirmation is provided (value=True)
    ctx = click.Context(test_cmd)
    # Should not raise any exception
    callback(ctx, option, True)


def test_confirmation_option_with_custom_param_decls():
    """Test that custom parameter declarations work correctly."""
    from click.decorators import confirmation_option
    
    @click.command()
    @confirmation_option('--confirm', '--yes')
    def test_cmd():
        click.echo("Command executed")
    
    runner = CliRunner()
    result = runner.invoke(test_cmd, ['--confirm'])
    assert result.exit_code == 0
    assert "Command executed" in result.output


def test_confirmation_option_default_param_decls():
    """Test that default parameter declarations are used when none provided."""
    from click.decorators import confirmation_option
    
    @click.command()
    @confirmation_option()
    def test_cmd():
        click.echo("Command executed")
    
    runner = CliRunner()
    result = runner.invoke(test_cmd, ['--yes'])
    assert result.exit_code == 0
    assert "Command executed" in result.output


def test_confirmation_option_with_prompt():
    """Test that the confirmation option prompts when flag is not provided."""
    from click.decorators import confirmation_option
    
    @click.command()
    @confirmation_option()
    def test_cmd():
        click.echo("Command executed")
    
    runner = CliRunner()
    
    # Test with prompt input 'n' (should abort)
    result = runner.invoke(test_cmd, input='n\n')
    assert result.exit_code == 1
    assert "Do you want to continue?" in result.output
    
    # Test with prompt input 'y' (should continue)
    result = runner.invoke(test_cmd, input='y\n')
    assert result.exit_code == 0
    assert "Command executed" in result.output


def test_confirmation_option_with_custom_kwargs():
    """Test that custom kwargs are properly passed to the option decorator."""
    from click.decorators import confirmation_option
    
    @click.command()
    @confirmation_option(help="Custom help text", prompt="Custom prompt?")
    def test_cmd():
        click.echo("Command executed")
    
    runner = CliRunner()
    
    # Test custom prompt
    result = runner.invoke(test_cmd, input='n\n')
    assert "Custom prompt?" in result.output
    
    # Test custom help
    result = runner.invoke(test_cmd, ['--help'])
    assert "Custom help text" in result.output
