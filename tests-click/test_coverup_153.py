# file: src/click/src/click/testing.py:270-277
# asked: {"lines": [270, 271, 274, 275, 276, 277], "branches": [[275, 276], [275, 277]]}
# gained: {"lines": [270, 271, 274, 275, 276, 277], "branches": [[275, 276], [275, 277]]}

import pytest
from click.testing import CliRunner
import collections.abc as cabc


class TestCliRunnerMakeEnv:
    def test_make_env_without_overrides(self):
        """Test make_env when no overrides are provided."""
        runner = CliRunner(env={"VAR1": "value1", "VAR2": "value2"})
        result = runner.make_env()
        assert result == {"VAR1": "value1", "VAR2": "value2"}
    
    def test_make_env_with_none_overrides(self):
        """Test make_env when overrides is None."""
        runner = CliRunner(env={"VAR1": "value1"})
        result = runner.make_env(None)
        assert result == {"VAR1": "value1"}
    
    def test_make_env_with_empty_overrides(self):
        """Test make_env when overrides is an empty dict."""
        runner = CliRunner(env={"VAR1": "value1"})
        result = runner.make_env({})
        assert result == {"VAR1": "value1"}
    
    def test_make_env_with_overrides(self):
        """Test make_env when overrides are provided."""
        runner = CliRunner(env={"VAR1": "value1", "VAR2": "value2"})
        overrides = {"VAR2": "new_value2", "VAR3": "value3"}
        result = runner.make_env(overrides)
        expected = {"VAR1": "value1", "VAR2": "new_value2", "VAR3": "value3"}
        assert result == expected
    
    def test_make_env_with_none_values_in_overrides(self):
        """Test make_env when overrides contain None values."""
        runner = CliRunner(env={"VAR1": "value1", "VAR2": "value2"})
        overrides = {"VAR1": None, "VAR3": "value3"}
        result = runner.make_env(overrides)
        expected = {"VAR1": None, "VAR2": "value2", "VAR3": "value3"}
        assert result == expected
    
    def test_make_env_empty_env_with_overrides(self):
        """Test make_env when runner has empty env and overrides are provided."""
        runner = CliRunner(env={})
        overrides = {"VAR1": "value1", "VAR2": "value2"}
        result = runner.make_env(overrides)
        assert result == overrides
    
    def test_make_env_no_env_with_overrides(self):
        """Test make_env when runner has no env (None) and overrides are provided."""
        runner = CliRunner(env=None)
        overrides = {"VAR1": "value1", "VAR2": "value2"}
        result = runner.make_env(overrides)
        assert result == overrides
