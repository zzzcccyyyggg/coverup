# file: src/click/src/click/core.py:2477-2520
# asked: {"lines": [2477, 2502, 2503, 2505, 2506, 2508, 2509, 2511, 2512, 2515, 2516, 2520], "branches": [[2502, 2503], [2502, 2505], [2505, 2506], [2505, 2511], [2508, 2509], [2508, 2520], [2511, 2512], [2511, 2520], [2515, 2511], [2515, 2516]]}
# gained: {"lines": [2477, 2502, 2503, 2505, 2506, 2508, 2509, 2511, 2512, 2515, 2516, 2520], "branches": [[2502, 2503], [2502, 2505], [2505, 2506], [2505, 2511], [2508, 2509], [2508, 2520], [2511, 2512], [2511, 2520], [2515, 2511], [2515, 2516]]}

import os
import pytest
from click.core import Context, Command
from click import Option

class TestParameterResolveEnvvarValue:
    """Test cases for Parameter.resolve_envvar_value method to achieve full coverage."""
    
    def test_resolve_envvar_value_no_envvar(self):
        """Test when envvar is not set - should return None."""
        param = Option(['--test'])
        param.envvar = None
        ctx = Context(Command('test'))
        
        result = param.resolve_envvar_value(ctx)
        assert result is None
    
    def test_resolve_envvar_value_single_envvar_not_set(self, monkeypatch):
        """Test when single envvar is set but not found in environment - should return None."""
        param = Option(['--test'])
        param.envvar = "TEST_VAR"
        ctx = Context(Command('test'))
        
        # Ensure the envvar is not set
        monkeypatch.delenv("TEST_VAR", raising=False)
        
        result = param.resolve_envvar_value(ctx)
        assert result is None
    
    def test_resolve_envvar_value_single_envvar_empty(self, monkeypatch):
        """Test when single envvar is set but has empty value - should return None."""
        param = Option(['--test'])
        param.envvar = "TEST_VAR"
        ctx = Context(Command('test'))
        
        # Set envvar with empty value
        monkeypatch.setenv("TEST_VAR", "")
        
        result = param.resolve_envvar_value(ctx)
        assert result is None
    
    def test_resolve_envvar_value_single_envvar_with_value(self, monkeypatch):
        """Test when single envvar is set and has non-empty value - should return the value."""
        param = Option(['--test'])
        param.envvar = "TEST_VAR"
        ctx = Context(Command('test'))
        
        # Set envvar with non-empty value
        test_value = "test_value"
        monkeypatch.setenv("TEST_VAR", test_value)
        
        result = param.resolve_envvar_value(ctx)
        assert result == test_value
    
    def test_resolve_envvar_value_multiple_envvars_all_not_set(self, monkeypatch):
        """Test when multiple envvars are set but none are found - should return None."""
        param = Option(['--test'])
        param.envvar = ["VAR1", "VAR2", "VAR3"]
        ctx = Context(Command('test'))
        
        # Ensure none of the envvars are set
        for var in param.envvar:
            monkeypatch.delenv(var, raising=False)
        
        result = param.resolve_envvar_value(ctx)
        assert result is None
    
    def test_resolve_envvar_value_multiple_envvars_all_empty(self, monkeypatch):
        """Test when multiple envvars are set but all have empty values - should return None."""
        param = Option(['--test'])
        param.envvar = ["VAR1", "VAR2", "VAR3"]
        ctx = Context(Command('test'))
        
        # Set all envvars with empty values
        for var in param.envvar:
            monkeypatch.setenv(var, "")
        
        result = param.resolve_envvar_value(ctx)
        assert result is None
    
    def test_resolve_envvar_value_multiple_envvars_first_has_value(self, monkeypatch):
        """Test when multiple envvars are set and first one has value - should return first value."""
        param = Option(['--test'])
        param.envvar = ["VAR1", "VAR2", "VAR3"]
        ctx = Context(Command('test'))
        
        # Set first envvar with value, others not set
        test_value = "first_value"
        monkeypatch.setenv("VAR1", test_value)
        monkeypatch.delenv("VAR2", raising=False)
        monkeypatch.delenv("VAR3", raising=False)
        
        result = param.resolve_envvar_value(ctx)
        assert result == test_value
    
    def test_resolve_envvar_value_multiple_envvars_second_has_value(self, monkeypatch):
        """Test when multiple envvars are set and second one has value - should return second value."""
        param = Option(['--test'])
        param.envvar = ["VAR1", "VAR2", "VAR3"]
        ctx = Context(Command('test'))
        
        # Set first envvar empty, second with value, third not set
        monkeypatch.setenv("VAR1", "")
        test_value = "second_value"
        monkeypatch.setenv("VAR2", test_value)
        monkeypatch.delenv("VAR3", raising=False)
        
        result = param.resolve_envvar_value(ctx)
        assert result == test_value
    
    def test_resolve_envvar_value_multiple_envvars_last_has_value(self, monkeypatch):
        """Test when multiple envvars are set and last one has value - should return last value."""
        param = Option(['--test'])
        param.envvar = ["VAR1", "VAR2", "VAR3"]
        ctx = Context(Command('test'))
        
        # Set first two envvars empty, last with value
        monkeypatch.setenv("VAR1", "")
        monkeypatch.setenv("VAR2", "")
        test_value = "last_value"
        monkeypatch.setenv("VAR3", test_value)
        
        result = param.resolve_envvar_value(ctx)
        assert result == test_value
    
    def test_resolve_envvar_value_multiple_envvars_mixed(self, monkeypatch):
        """Test when multiple envvars are set with mixed states - should return first non-empty."""
        param = Option(['--test'])
        param.envvar = ["VAR1", "VAR2", "VAR3"]
        ctx = Context(Command('test'))
        
        # Set first envvar not set, second with value, third also with value
        monkeypatch.delenv("VAR1", raising=False)
        test_value = "second_value"
        monkeypatch.setenv("VAR2", test_value)
        monkeypatch.setenv("VAR3", "third_value")
        
        result = param.resolve_envvar_value(ctx)
        assert result == test_value
