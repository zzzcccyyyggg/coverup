# file: src/click/src/click/testing.py:251-261
# asked: {"lines": [251, 253, 254, 255, 256, 258, 259, 260, 261], "branches": []}
# gained: {"lines": [251, 253, 254, 255, 256, 258, 259, 260, 261], "branches": []}

import pytest
from click.testing import CliRunner

def test_cli_runner_init_with_env():
    """Test CliRunner initialization with custom environment variables."""
    env = {"TEST_VAR": "test_value", "ANOTHER_VAR": None}
    runner = CliRunner(env=env)
    assert runner.env == env
    assert runner.charset == "utf-8"
    assert runner.echo_stdin is False
    assert runner.catch_exceptions is True

def test_cli_runner_init_without_env():
    """Test CliRunner initialization without environment variables."""
    runner = CliRunner()
    assert runner.env == {}
    assert runner.charset == "utf-8"
    assert runner.echo_stdin is False
    assert runner.catch_exceptions is True

def test_cli_runner_init_with_custom_charset():
    """Test CliRunner initialization with custom charset."""
    runner = CliRunner(charset="iso-8859-1")
    assert runner.charset == "iso-8859-1"
    assert runner.env == {}
    assert runner.echo_stdin is False
    assert runner.catch_exceptions is True

def test_cli_runner_init_with_echo_stdin():
    """Test CliRunner initialization with echo_stdin enabled."""
    runner = CliRunner(echo_stdin=True)
    assert runner.echo_stdin is True
    assert runner.charset == "utf-8"
    assert runner.env == {}
    assert runner.catch_exceptions is True

def test_cli_runner_init_with_catch_exceptions_false():
    """Test CliRunner initialization with catch_exceptions disabled."""
    runner = CliRunner(catch_exceptions=False)
    assert runner.catch_exceptions is False
    assert runner.charset == "utf-8"
    assert runner.env == {}
    assert runner.echo_stdin is False
