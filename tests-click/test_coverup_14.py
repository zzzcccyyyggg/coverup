# file: src/click/src/click/testing.py:433-544
# asked: {"lines": [433, 436, 437, 438, 439, 440, 486, 487, 488, 490, 491, 492, 493, 495, 496, 498, 499, 500, 501, 503, 504, 505, 506, 507, 509, 510, 512, 513, 515, 516, 517, 518, 520, 522, 523, 524, 525, 526, 527, 529, 530, 531, 532, 533, 535, 536, 537, 538, 539, 540, 541, 542, 543], "branches": [[487, 488], [487, 490], [495, 496], [495, 498], [509, 510], [509, 512], [512, 513], [512, 515], [515, 516], [515, 520], [523, 524], [523, 525]]}
# gained: {"lines": [433, 436, 437, 438, 439, 440, 486, 487, 488, 490, 491, 492, 493, 495, 496, 498, 499, 500, 501, 503, 504, 505, 506, 507, 509, 510, 512, 513, 515, 516, 517, 518, 520, 522, 523, 524, 525, 526, 527, 529, 530, 531, 532, 533, 535, 536, 537, 538, 539, 540, 541, 542, 543], "branches": [[487, 488], [487, 490], [495, 496], [495, 498], [509, 510], [509, 512], [512, 513], [512, 515], [515, 516], [515, 520], [523, 524], [523, 525]]}

import pytest
import click
from click.testing import CliRunner, Result
import sys
from unittest.mock import Mock, patch

def test_invoke_with_string_args():
    """Test that string args are properly split using shlex.split"""
    @click.command()
    @click.argument('name')
    def test_cmd(name):
        click.echo(f"Hello {name}")
    
    runner = CliRunner()
    result = runner.invoke(test_cmd, "test")
    assert result.exit_code == 0
    assert "Hello test" in result.stdout

def test_invoke_with_prog_name_in_extra():
    """Test that prog_name is properly extracted from extra kwargs"""
    @click.command()
    def test_cmd():
        click.echo("Hello World")
    
    runner = CliRunner()
    result = runner.invoke(test_cmd, prog_name="custom_prog")
    assert result.exit_code == 0

def test_invoke_system_exit_with_none_code():
    """Test SystemExit with None code (should become exit code 0)"""
    @click.command()
    def test_cmd():
        sys.exit(None)
    
    runner = CliRunner()
    result = runner.invoke(test_cmd)
    assert result.exit_code == 0
    assert result.exception is None

def test_invoke_system_exit_with_non_zero_int_code():
    """Test SystemExit with non-zero integer code"""
    @click.command()
    def test_cmd():
        sys.exit(42)
    
    runner = CliRunner()
    result = runner.invoke(test_cmd)
    assert result.exit_code == 42
    assert isinstance(result.exception, SystemExit)

def test_invoke_system_exit_with_non_int_code():
    """Test SystemExit with non-integer code (should write to stdout and become exit code 1)"""
    @click.command()
    def test_cmd():
        sys.exit("error message")
    
    runner = CliRunner()
    result = runner.invoke(test_cmd)
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "error message" in result.stdout

def test_invoke_with_exception_and_catch_exceptions_false():
    """Test that exceptions are raised when catch_exceptions=False"""
    @click.command()
    def test_cmd():
        raise ValueError("test error")
    
    runner = CliRunner(catch_exceptions=False)
    with pytest.raises(ValueError, match="test error"):
        runner.invoke(test_cmd)

def test_invoke_with_exception_and_catch_exceptions_true():
    """Test that exceptions are caught when catch_exceptions=True"""
    @click.command()
    def test_cmd():
        raise ValueError("test error")
    
    runner = CliRunner(catch_exceptions=True)
    result = runner.invoke(test_cmd)
    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert result.exc_info is not None

def test_invoke_with_exception_and_catch_exceptions_override_false():
    """Test that exceptions are raised when catch_exceptions parameter overrides to False"""
    @click.command()
    def test_cmd():
        raise ValueError("test error")
    
    runner = CliRunner(catch_exceptions=True)
    with pytest.raises(ValueError, match="test error"):
        runner.invoke(test_cmd, catch_exceptions=False)

def test_invoke_with_exception_and_catch_exceptions_override_true():
    """Test that exceptions are caught when catch_exceptions parameter overrides to True"""
    @click.command()
    def test_cmd():
        raise ValueError("test error")
    
    runner = CliRunner(catch_exceptions=False)
    result = runner.invoke(test_cmd, catch_exceptions=True)
    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)

def test_invoke_with_return_value():
    """Test that return_value is properly captured from command"""
    @click.command()
    def test_cmd():
        return "custom return value"
    
    runner = CliRunner()
    result = runner.invoke(test_cmd, standalone_mode=False)
    assert result.exit_code == 0
    assert result.return_value == "custom return value"

def test_invoke_with_empty_args():
    """Test invoke with None args"""
    @click.command()
    def test_cmd():
        click.echo("Hello World")
    
    runner = CliRunner()
    result = runner.invoke(test_cmd, args=None)
    assert result.exit_code == 0
    assert "Hello World" in result.stdout

def test_invoke_with_sequence_args():
    """Test invoke with sequence args"""
    @click.command()
    @click.argument('name')
    def test_cmd(name):
        click.echo(f"Hello {name}")
    
    runner = CliRunner()
    result = runner.invoke(test_cmd, args=["test_name"])
    assert result.exit_code == 0
    assert "Hello test_name" in result.stdout

def test_invoke_with_custom_catch_exceptions_none():
    """Test that None catch_exceptions uses runner's default"""
    @click.command()
    def test_cmd():
        raise ValueError("test error")
    
    runner = CliRunner(catch_exceptions=True)
    result = runner.invoke(test_cmd, catch_exceptions=None)
    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)

def test_invoke_with_system_exit_zero():
    """Test SystemExit with code 0"""
    @click.command()
    def test_cmd():
        sys.exit(0)
    
    runner = CliRunner()
    result = runner.invoke(test_cmd)
    assert result.exit_code == 0
    assert result.exception is None
