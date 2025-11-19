# file: src/click/src/click/core.py:533-559
# asked: {"lines": [533, 534, 559], "branches": []}
# gained: {"lines": [533, 534, 559], "branches": []}

import pytest
import click
from click.core import Context


class TestContextMetaProperty:
    def test_meta_property_returns_meta_dict(self):
        """Test that the meta property returns the _meta dictionary."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context with a parent that has meta data
        parent_meta = {'parent.key': 'parent_value'}
        parent_ctx = Context(mock_command)
        parent_ctx._meta = parent_meta
        
        # Create a child context
        child_ctx = Context(mock_command, parent=parent_ctx)
        
        # Test that the meta property returns the shared meta dictionary
        assert child_ctx.meta is parent_meta
        assert child_ctx.meta['parent.key'] == 'parent_value'
        
    def test_meta_property_without_parent(self):
        """Test that the meta property works correctly without a parent context."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context without a parent
        ctx = Context(mock_command)
        
        # The meta property should return the _meta dictionary
        assert ctx.meta == {}
        assert isinstance(ctx.meta, dict)
        
    def test_meta_property_is_shared_across_nested_contexts(self):
        """Test that the meta dictionary is shared across nested contexts."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a root context
        root_ctx = Context(mock_command)
        root_meta = root_ctx.meta
        
        # Create nested contexts
        child_ctx = Context(mock_command, parent=root_ctx)
        grandchild_ctx = Context(mock_command, parent=child_ctx)
        
        # All contexts should share the same meta dictionary
        assert root_ctx.meta is child_ctx.meta
        assert child_ctx.meta is grandchild_ctx.meta
        assert root_ctx.meta is grandchild_ctx.meta
        
        # Modifications in one context should be visible in others
        root_ctx.meta['shared.key'] = 'shared_value'
        assert child_ctx.meta['shared.key'] == 'shared_value'
        assert grandchild_ctx.meta['shared.key'] == 'shared_value'
        
    def test_meta_property_example_usage_pattern(self):
        """Test the example usage pattern from the docstring."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context
        ctx = Context(mock_command)
        
        # Simulate the example usage pattern
        LANG_KEY = f'{__name__}.lang'
        
        def set_language(value):
            ctx.meta[LANG_KEY] = value
            
        def get_language():
            return ctx.meta.get(LANG_KEY, 'en_US')
        
        # Test the functions work as expected
        assert get_language() == 'en_US'  # Default value
        
        set_language('fr_FR')
        assert get_language() == 'fr_FR'
        
        # Verify the value is stored in meta
        assert ctx.meta[LANG_KEY] == 'fr_FR'
