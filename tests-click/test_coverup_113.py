# file: src/click/src/click/core.py:3192-3232
# asked: {"lines": [3192, 3205, 3208, 3209, 3214, 3217, 3218, 3221, 3224, 3225, 3226, 3227, 3228, 3230, 3232], "branches": [[3208, 3209], [3208, 3214], [3214, 3217], [3214, 3224], [3217, 3218], [3217, 3221], [3225, 3226], [3225, 3232], [3227, 3228], [3227, 3230]]}
# gained: {"lines": [3192, 3205, 3208, 3209, 3214, 3217, 3218, 3221, 3224, 3225, 3226, 3227, 3228, 3230, 3232], "branches": [[3208, 3209], [3208, 3214], [3214, 3217], [3214, 3224], [3217, 3218], [3217, 3221], [3225, 3226], [3225, 3232], [3227, 3228], [3227, 3230]]}

import pytest
import typing as t
from click.core import Context, Option, Command
from click import types
from click._utils import UNSET


class MockCommand(Command):
    """A mock command for testing purposes."""
    def __init__(self, name="test_command"):
        super().__init__(name=name)


class TestOptionValueFromEnvvar:
    """Test cases for Option.value_from_envvar method to achieve full coverage."""
    
    def test_value_from_envvar_none_when_envvar_not_set(self, monkeypatch):
        """Test that None is returned when environment variable is not set."""
        ctx = Context(MockCommand())
        opt = Option(['--test'])
        
        # Mock resolve_envvar_value to return None
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: None)
        
        result = opt.value_from_envvar(ctx)
        assert result is None
    
    def test_value_from_envvar_flag_non_bool_with_flag_value_match(self, monkeypatch):
        """Test non-boolean flag with flag_value matching envvar value."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], is_flag=True, flag_value='custom_flag')
        
        # Mock resolve_envvar_value to return the flag_value
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'custom_flag')
        
        result = opt.value_from_envvar(ctx)
        assert result == 'custom_flag'
    
    def test_value_from_envvar_flag_non_bool_with_flag_value_mismatch(self, monkeypatch):
        """Test non-boolean flag with flag_value not matching envvar value."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], is_flag=True, flag_value='custom_flag')
        
        # Mock resolve_envvar_value to return a different value
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'yes')
        
        result = opt.value_from_envvar(ctx)
        assert result is True  # 'yes' should convert to True
    
    def test_value_from_envvar_flag_non_bool_without_flag_value(self, monkeypatch):
        """Test non-boolean flag without flag_value set."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], is_flag=True)
        
        # Mock resolve_envvar_value to return 'true'
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'true')
        
        result = opt.value_from_envvar(ctx)
        # When is_flag=True but flag_value is UNSET, it should return the raw value
        assert result == 'true'
    
    def test_value_from_envvar_repeated_options_nargs_1_multiple_true(self, monkeypatch):
        """Test repeated options with nargs=1 and multiple=True."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], multiple=True, type=str)
        
        # Mock resolve_envvar_value to return a space-separated string
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'value1 value2 value3')
        
        # Mock the type's split_envvar_value method
        mock_type = types.StringParamType()
        monkeypatch.setattr(opt, 'type', mock_type)
        
        result = opt.value_from_envvar(ctx)
        assert result == ['value1', 'value2', 'value3']
    
    def test_value_from_envvar_repeated_options_nargs_gt_1_multiple_true(self, monkeypatch):
        """Test repeated options with nargs>1 and multiple=True."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], nargs=2, multiple=True, type=str)
        
        # Mock resolve_envvar_value to return a space-separated string
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'a b c d')
        
        # Mock the type's split_envvar_value method
        mock_type = types.StringParamType()
        monkeypatch.setattr(opt, 'type', mock_type)
        
        result = opt.value_from_envvar(ctx)
        # Should be batched into tuples of 2
        assert result == [('a', 'b'), ('c', 'd')]
    
    def test_value_from_envvar_repeated_options_nargs_gt_1_multiple_false(self, monkeypatch):
        """Test repeated options with nargs>1 and multiple=False."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], nargs=2, multiple=False, type=str)
        
        # Mock resolve_envvar_value to return a space-separated string
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'x y')
        
        # Mock the type's split_envvar_value method
        mock_type = types.StringParamType()
        monkeypatch.setattr(opt, 'type', mock_type)
        
        result = opt.value_from_envvar(ctx)
        # Should be split but not batched since multiple=False
        assert result == ['x', 'y']
    
    def test_value_from_envvar_simple_value_depth_0(self, monkeypatch):
        """Test simple case where value_depth is 0 (nargs=1, multiple=False)."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], type=str)
        
        # Mock resolve_envvar_value to return a simple string
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'simple_value')
        
        result = opt.value_from_envvar(ctx)
        assert result == 'simple_value'
    
    def test_value_from_envvar_bool_flag_with_envvar(self, monkeypatch):
        """Test boolean flag with environment variable set."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], is_flag=True)
        
        # Mock resolve_envvar_value to return 'true'
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'true')
        
        result = opt.value_from_envvar(ctx)
        # Boolean flags should return the raw value for processing
        assert result == 'true'
    
    def test_value_from_envvar_flag_non_bool_with_false_string(self, monkeypatch):
        """Test non-boolean flag with false string value."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], is_flag=True, flag_value='custom_flag')
        
        # Mock resolve_envvar_value to return 'false'
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'false')
        
        result = opt.value_from_envvar(ctx)
        assert result is False  # 'false' should convert to False
    
    def test_value_from_envvar_flag_non_bool_with_unknown_string(self, monkeypatch):
        """Test non-boolean flag with unknown string value."""
        ctx = Context(MockCommand())
        opt = Option(['--test'], is_flag=True, flag_value='custom_flag')
        
        # Mock resolve_envvar_value to return unknown value
        monkeypatch.setattr(opt, 'resolve_envvar_value', lambda ctx: 'unknown_value')
        
        result = opt.value_from_envvar(ctx)
        assert result is None  # unknown value should convert to None
