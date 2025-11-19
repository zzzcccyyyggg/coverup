# file: src/click/src/click/core.py:2253-2256
# asked: {"lines": [2253, 2254, 2255, 2256], "branches": []}
# gained: {"lines": [2253, 2254, 2255], "branches": []}

import pytest
import click
from click.core import Context, Option
from click._utils import UNSET

class TestParameterGetDefault:
    def test_get_default_with_call_false_returns_callable(self):
        """Test that get_default with call=False returns a callable when default is callable."""
        ctx = Context(click.Command('test'))
        
        def default_func():
            return "default_value"
        
        param = Option(['--test'], default=default_func)
        
        # Test with call=False - should return the callable
        result = param.get_default(ctx, call=False)
        assert result is default_func
        assert callable(result)
        
        # Test with call=True - should return the result of calling the callable
        result_with_call = param.get_default(ctx, call=True)
        assert result_with_call == "default_value"
        assert not callable(result_with_call)

    def test_get_default_with_call_false_returns_non_callable(self):
        """Test that get_default with call=False returns non-callable default as-is."""
        ctx = Context(click.Command('test'))
        
        param = Option(['--test'], default="static_default")
        
        # Test with call=False - should return the static value
        result = param.get_default(ctx, call=False)
        assert result == "static_default"
        assert not callable(result)
        
        # Test with call=True - should return the same static value
        result_with_call = param.get_default(ctx, call=True)
        assert result_with_call == "static_default"
        assert not callable(result_with_call)

    def test_get_default_with_no_default_returns_unset(self):
        """Test that get_default returns UNSET when no default is set."""
        ctx = Context(click.Command('test'))
        
        param = Option(['--test'])
        
        # Test with call=False - should return UNSET
        result = param.get_default(ctx, call=False)
        assert result is UNSET
        
        # Test with call=True - should return UNSET
        result_with_call = param.get_default(ctx, call=True)
        assert result_with_call is UNSET
