# file: src/click/src/click/core.py:688-691
# asked: {"lines": [688, 689, 690, 691], "branches": []}
# gained: {"lines": [688, 689, 690], "branches": []}

import pytest
import typing as t
from click.core import Context, Command

class MockCommand(Command):
    """A minimal mock command for testing Context"""
    def __init__(self, name="test_command"):
        super().__init__(name=name)

class TestContextLookupDefault:
    def test_lookup_default_overload_true(self):
        """Test the @overload decorator for lookup_default with call=True"""
        # Create a Context with a mock command
        mock_command = MockCommand()
        ctx = Context(command=mock_command)
        
        # The overload decorator itself doesn't execute the function body,
        # but we can verify the signature exists by checking the method
        assert hasattr(ctx, 'lookup_default')
        assert callable(ctx.lookup_default)
        
        # The overload decorator creates a special attribute that we can check
        # This ensures the overload signature is properly defined
        import inspect
        sig = inspect.signature(ctx.lookup_default)
        assert 'name' in sig.parameters
        assert 'call' in sig.parameters
        assert sig.parameters['call'].default is True
