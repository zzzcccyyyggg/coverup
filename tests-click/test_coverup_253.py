# file: src/click/src/click/core.py:2522-2536
# asked: {"lines": [2522, 2531, 2533, 2534, 2536], "branches": [[2533, 2534], [2533, 2536]]}
# gained: {"lines": [2522], "branches": []}

import pytest
import click
from click.core import Context
from click.types import ParamType


class MockParamType(ParamType):
    """A mock parameter type for testing split_envvar_value."""
    name = "mock"
    
    def split_envvar_value(self, rv: str):
        """Split environment variable value by commas for testing."""
        return rv.split(',')


def test_value_from_envvar_nargs_1_returns_raw_value(monkeypatch):
    """Test value_from_envvar when nargs=1 returns raw value."""
    # Create a mock context
    ctx = Context(click.Command('test'))
    
    # Create an Option with nargs=1 (Option implements _parse_decls)
    param = click.Option(['--test'], nargs=1)
    param.type = MockParamType()
    
    # Mock resolve_envvar_value to return a string
    monkeypatch.setattr(param, 'resolve_envvar_value', lambda ctx: "test_value")
    
    # Test that the raw value is returned when nargs=1
    result = param.value_from_envvar(ctx)
    assert result == "test_value"


def test_value_from_envvar_nargs_not_1_splits_value(monkeypatch):
    """Test value_from_envvar when nargs != 1 splits the environment variable value."""
    # Create a mock context
    ctx = Context(click.Command('test'))
    
    # Create an Option with nargs=2 (not 1)
    param = click.Option(['--test'], nargs=2)
    param.type = MockParamType()
    
    # Mock resolve_envvar_value to return a string that can be split
    monkeypatch.setattr(param, 'resolve_envvar_value', lambda ctx: "val1,val2,val3")
    
    # Test that the value is split when nargs != 1
    result = param.value_from_envvar(ctx)
    assert result == ["val1", "val2", "val3"]


def test_value_from_envvar_none_returns_none(monkeypatch):
    """Test value_from_envvar returns None when resolve_envvar_value returns None."""
    # Create a mock context
    ctx = Context(click.Command('test'))
    
    # Create an Option with nargs=2
    param = click.Option(['--test'], nargs=2)
    param.type = MockParamType()
    
    # Mock resolve_envvar_value to return None
    monkeypatch.setattr(param, 'resolve_envvar_value', lambda ctx: None)
    
    # Test that None is returned when resolve_envvar_value returns None
    result = param.value_from_envvar(ctx)
    assert result is None


def test_value_from_envvar_nargs_not_1_with_none_returns_none(monkeypatch):
    """Test value_from_envvar when nargs != 1 but resolve_envvar_value returns None."""
    # Create a mock context
    ctx = Context(click.Command('test'))
    
    # Create an Option with nargs=2
    param = click.Option(['--test'], nargs=2)
    param.type = MockParamType()
    
    # Mock resolve_envvar_value to return None
    monkeypatch.setattr(param, 'resolve_envvar_value', lambda ctx: None)
    
    # Test that None is returned even when nargs != 1
    result = param.value_from_envvar(ctx)
    assert result is None
