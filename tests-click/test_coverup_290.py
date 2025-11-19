# file: src/click/src/click/testing.py:263-268
# asked: {"lines": [263, 268], "branches": []}
# gained: {"lines": [263, 268], "branches": []}

import pytest
from click.core import Command
from click.testing import CliRunner

class TestCliRunnerGetDefaultProgName:
    def test_get_default_prog_name_with_name(self):
        """Test get_default_prog_name when command has a name."""
        runner = CliRunner()
        cmd = Command(name="test_command")
        result = runner.get_default_prog_name(cmd)
        assert result == "test_command"

    def test_get_default_prog_name_without_name(self):
        """Test get_default_prog_name when command has no name (None)."""
        runner = CliRunner()
        cmd = Command(name=None)
        result = runner.get_default_prog_name(cmd)
        assert result == "root"

    def test_get_default_prog_name_with_empty_string_name(self):
        """Test get_default_prog_name when command has empty string name."""
        runner = CliRunner()
        cmd = Command(name="")
        result = runner.get_default_prog_name(cmd)
        assert result == "root"
