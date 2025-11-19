# file: src/click/src/click/core.py:2248-2251
# asked: {"lines": [2248, 2249, 2250, 2251], "branches": []}
# gained: {"lines": [2248, 2249, 2250], "branches": []}

import pytest
import typing as t
from click.core import Context, Option
from click import Command
from click._utils import UNSET

class TestParameterGetDefault:
    def test_get_default_with_call_true_overload(self):
        """Test that the overload with call=True is properly exercised."""
        # Create a mock context
        ctx = Context(Command('test'))
        
        # Create an Option with a default value (Option implements _parse_decls)
        param = Option(param_decls=['--test'], default='default_value')
        
        # Call get_default with call=True (the literal True)
        result = param.get_default(ctx, call=True)
        
        # Verify the result is the default value (not the callable)
        assert result == 'default_value'
    
    def test_get_default_with_call_false_overload(self):
        """Test that the overload with call=False is properly exercised."""
        # Create a mock context
        ctx = Context(Command('test'))
        
        # Create an Option with a callable default
        def default_func():
            return 'callable_default'
        
        param = Option(param_decls=['--test'], default=default_func)
        
        # Call get_default with call=False
        result = param.get_default(ctx, call=False)
        
        # Verify the result is the callable itself
        assert result == default_func
    
    def test_get_default_with_call_true_and_callable_default(self):
        """Test that call=True with a callable default executes the callable."""
        # Create a mock context
        ctx = Context(Command('test'))
        
        # Create an Option with a callable default
        def default_func():
            return 'callable_default'
        
        param = Option(param_decls=['--test'], default=default_func)
        
        # Call get_default with call=True
        result = param.get_default(ctx, call=True)
        
        # Verify the result is the executed callable's return value
        assert result == 'callable_default'
    
    def test_get_default_with_call_true_and_none_default(self):
        """Test that call=True with None default returns None."""
        # Create a mock context
        ctx = Context(Command('test'))
        
        # Create an Option with None default
        param = Option(param_decls=['--test'], default=None)
        
        # Call get_default with call=True
        result = param.get_default(ctx, call=True)
        
        # Verify the result is None
        assert result is None
    
    def test_get_default_with_call_true_and_no_default(self):
        """Test that call=True with no default returns UNSET."""
        # Create a mock context
        ctx = Context(Command('test'))
        
        # Create an Option without default (uses UNSET internally)
        param = Option(param_decls=['--test'])
        
        # Call get_default with call=True
        result = param.get_default(ctx, call=True)
        
        # Verify the result is UNSET when no default is set
        assert result is UNSET
