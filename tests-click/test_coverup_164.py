# file: src/click/src/click/core.py:2258-2289
# asked: {"lines": [2258, 2259, 2281, 2283, 2284, 2286, 2287, 2289], "branches": [[2283, 2284], [2283, 2286], [2286, 2287], [2286, 2289]]}
# gained: {"lines": [2258, 2259, 2281, 2283, 2284, 2286, 2287, 2289], "branches": [[2283, 2284], [2283, 2286], [2286, 2287], [2286, 2289]]}

import pytest
import typing as t
from click.core import Context, Option
from click._utils import UNSET

class MockCommand:
    def __init__(self):
        self.allow_extra_args = False
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False

class TestParameterGetDefault:
    def test_get_default_from_ctx_lookup_default(self):
        """Test when ctx.lookup_default returns a value (not UNSET)"""
        ctx = Context(MockCommand())
        param = Option(['--test'])
        
        # Mock ctx.lookup_default to return a specific value
        def mock_lookup_default(name, call=False):
            return "from_ctx_default"
        
        ctx.lookup_default = mock_lookup_default
        
        result = param.get_default(ctx)
        assert result == "from_ctx_default"

    def test_get_default_from_param_default_when_ctx_returns_unset(self):
        """Test when ctx.lookup_default returns UNSET and param.default is used"""
        ctx = Context(MockCommand())
        param = Option(['--test'], default="param_default")
        
        # Mock ctx.lookup_default to return UNSET
        def mock_lookup_default(name, call=False):
            return UNSET
        
        ctx.lookup_default = mock_lookup_default
        
        result = param.get_default(ctx)
        assert result == "param_default"

    def test_get_default_with_callable_and_call_true(self):
        """Test when default is callable and call=True (should call the callable)"""
        ctx = Context(MockCommand())
        
        callable_called = []
        def callable_default():
            callable_called.append(True)
            return "called_result"
        
        param = Option(['--test'], default=callable_default)
        
        result = param.get_default(ctx, call=True)
        assert result == "called_result"
        assert len(callable_called) == 1

    def test_get_default_with_callable_and_call_false(self):
        """Test when default is callable and call=False (should return the callable)"""
        ctx = Context(MockCommand())
        
        def callable_default():
            return "would_be_called"
        
        param = Option(['--test'], default=callable_default)
        
        result = param.get_default(ctx, call=False)
        assert result == callable_default
        assert callable(result)

    def test_get_default_none_when_both_unset(self):
        """Test when both ctx.lookup_default and param.default are UNSET/None"""
        ctx = Context(MockCommand())
        param = Option(['--test'], default=None)
        
        # Mock ctx.lookup_default to return UNSET
        def mock_lookup_default(name, call=False):
            return UNSET
        
        ctx.lookup_default = mock_lookup_default
        
        result = param.get_default(ctx)
        assert result is None

    def test_get_default_with_ctx_default_map(self):
        """Test when ctx has default_map that provides a value"""
        ctx = Context(MockCommand(), default_map={"test": "from_default_map"})
        param = Option(['--test'], default="param_default")
        
        result = param.get_default(ctx)
        assert result == "from_default_map"

    def test_get_default_callable_from_ctx(self):
        """Test when ctx.lookup_default returns a callable and call=True"""
        ctx = Context(MockCommand())
        param = Option(['--test'])
        
        callable_called = []
        def ctx_callable():
            callable_called.append(True)
            return "ctx_called_result"
        
        # Mock ctx.lookup_default to return a callable
        def mock_lookup_default(name, call=False):
            if call:
                return ctx_callable()
            return ctx_callable
        
        ctx.lookup_default = mock_lookup_default
        
        result = param.get_default(ctx, call=True)
        assert result == "ctx_called_result"
        assert len(callable_called) == 1

    def test_get_default_callable_from_ctx_with_call_false(self):
        """Test when ctx.lookup_default returns a callable and call=False"""
        ctx = Context(MockCommand())
        param = Option(['--test'])
        
        def ctx_callable():
            return "would_be_called"
        
        # Mock ctx.lookup_default to return a callable
        def mock_lookup_default(name, call=False):
            return ctx_callable
        
        ctx.lookup_default = mock_lookup_default
        
        result = param.get_default(ctx, call=False)
        assert result == ctx_callable
        assert callable(result)
