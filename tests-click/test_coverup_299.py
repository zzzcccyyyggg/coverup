# file: src/click/src/click/core.py:693-696
# asked: {"lines": [693, 694, 695, 696], "branches": []}
# gained: {"lines": [693, 694, 695], "branches": []}

import pytest
import click
from click.core import Context

class TestContext:
    def test_lookup_default_with_call_false(self):
        """Test lookup_default with call=False to cover the overload signature."""
        # Create a mock command
        class MockCommand(click.Command):
            def __init__(self):
                super().__init__('test')
        
        # Create context with default_map
        ctx = Context(MockCommand())
        ctx.default_map = {'test_param': 'default_value'}
        
        # Test lookup_default with call=False
        result = ctx.lookup_default('test_param', call=False)
        assert result == 'default_value'
        
        # Test with non-existent parameter - should return UNSET sentinel
        result = ctx.lookup_default('non_existent', call=False)
        # Check that it's the UNSET sentinel, not None
        assert result is not None
        assert hasattr(result, '__class__')
        assert result.__class__.__name__ == 'Sentinel'

    def test_lookup_default_with_call_false_callable(self):
        """Test lookup_default with call=False when default is callable."""
        # Create a mock command
        class MockCommand(click.Command):
            def __init__(self):
                super().__init__('test')
        
        # Create context with callable default
        ctx = Context(MockCommand())
        
        def default_func():
            return 'dynamic_value'
        
        ctx.default_map = {'test_param': default_func}
        
        # Test lookup_default with call=False should return the callable
        result = ctx.lookup_default('test_param', call=False)
        assert result == default_func
        assert callable(result)
        
        # Verify it's not called when call=False
        assert result() == 'dynamic_value'

    def test_lookup_default_with_call_false_no_default_map(self):
        """Test lookup_default with call=False when no default_map exists."""
        # Create a mock command
        class MockCommand(click.Command):
            def __init__(self):
                super().__init__('test')
        
        # Create context without default_map
        ctx = Context(MockCommand())
        ctx.default_map = None
        
        # Test lookup_default with call=False - should return UNSET sentinel
        result = ctx.lookup_default('test_param', call=False)
        # Check that it's the UNSET sentinel, not None
        assert result is not None
        assert hasattr(result, '__class__')
        assert result.__class__.__name__ == 'Sentinel'

    def test_lookup_default_with_call_false_empty_default_map(self):
        """Test lookup_default with call=False when default_map is empty."""
        # Create a mock command
        class MockCommand(click.Command):
            def __init__(self):
                super().__init__('test')
        
        # Create context with empty default_map
        ctx = Context(MockCommand())
        ctx.default_map = {}
        
        # Test lookup_default with call=False - should return UNSET sentinel
        result = ctx.lookup_default('test_param', call=False)
        # Check that it's the UNSET sentinel, not None
        assert result is not None
        assert hasattr(result, '__class__')
        assert result.__class__.__name__ == 'Sentinel'
