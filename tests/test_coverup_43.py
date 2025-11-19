# file: src/flask/src/flask/testing.py:265-298
# asked: {"lines": [265, 266, 271, 272, 273, 275, 276, 292, 293, 295, 296, 298], "branches": [[292, 293], [292, 295], [295, 296], [295, 298]]}
# gained: {"lines": [265, 266, 271, 272, 273, 275, 276, 292, 293, 295, 296, 298], "branches": [[292, 293], [292, 295], [295, 296], [295, 298]]}

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner
from click.testing import Result
import click

def test_flask_cli_runner_init():
    """Test FlaskCliRunner initialization."""
    app = Flask(__name__)
    runner = FlaskCliRunner(app)
    assert runner.app is app

def test_flask_cli_runner_invoke_with_default_cli():
    """Test FlaskCliRunner.invoke when cli is None (uses app.cli)."""
    app = Flask(__name__)
    
    @app.cli.command("test_command")
    def test_command():
        click.echo("Test command executed")
    
    runner = FlaskCliRunner(app)
    result = runner.invoke(args=["test_command"])
    assert result.exit_code == 0
    assert "Test command executed" in result.output

def test_flask_cli_runner_invoke_with_custom_cli():
    """Test FlaskCliRunner.invoke when custom cli is provided."""
    app = Flask(__name__)
    
    custom_cli = click.Group("custom")
    
    @custom_cli.command("custom_command")
    def custom_command():
        click.echo("Custom command executed")
    
    runner = FlaskCliRunner(app)
    result = runner.invoke(cli=custom_cli, args=["custom_command"])
    assert result.exit_code == 0
    assert "Custom command executed" in result.output

def test_flask_cli_runner_invoke_with_obj_provided():
    """Test FlaskCliRunner.invoke when obj is already provided in kwargs."""
    app = Flask(__name__)
    
    @app.cli.command("test_command")
    def test_command():
        click.echo("Test command with custom obj")
    
    runner = FlaskCliRunner(app)
    
    # Create a custom ScriptInfo object
    from flask.cli import ScriptInfo
    custom_obj = ScriptInfo(create_app=lambda: app)
    
    result = runner.invoke(args=["test_command"], obj=custom_obj)
    assert result.exit_code == 0
    assert "Test command with custom obj" in result.output

def test_flask_cli_runner_invoke_with_additional_kwargs():
    """Test FlaskCliRunner.invoke with additional kwargs passed to parent invoke."""
    app = Flask(__name__)
    
    @app.cli.command("test_command")
    def test_command():
        click.echo("Test command with input")
    
    runner = FlaskCliRunner(app)
    
    # Test with input parameter
    result = runner.invoke(args=["test_command"], input="test_input\n")
    assert result.exit_code == 0
    assert "Test command with input" in result.output

def test_flask_cli_runner_invoke_error_case():
    """Test FlaskCliRunner.invoke with a command that fails."""
    app = Flask(__name__)
    
    @app.cli.command("failing_command")
    def failing_command():
        raise click.ClickException("Command failed")
    
    runner = FlaskCliRunner(app)
    result = runner.invoke(args=["failing_command"])
    assert result.exit_code != 0
    assert "Command failed" in result.output

def test_flask_cli_runner_invoke_with_env():
    """Test FlaskCliRunner.invoke with environment variables."""
    app = Flask(__name__)
    
    @app.cli.command("env_command")
    def env_command():
        import os
        click.echo(f"ENV_VAR: {os.environ.get('TEST_ENV_VAR', 'not_set')}")
    
    runner = FlaskCliRunner(app)
    result = runner.invoke(args=["env_command"], env={"TEST_ENV_VAR": "test_value"})
    assert result.exit_code == 0
    assert "ENV_VAR: test_value" in result.output
