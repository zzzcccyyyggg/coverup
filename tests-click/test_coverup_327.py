# file: src/click/src/click/core.py:752-758
# asked: {"lines": [752, 758], "branches": []}
# gained: {"lines": [752, 758], "branches": []}

import pytest
import click
from click.core import Context, Command

class TestContext:
    """Test class for Context._make_sub_context method"""
    
    def test_make_sub_context_creates_correct_type(self):
        """Test that _make_sub_context creates a context of the same type as the parent"""
        # Create a parent context with a command
        parent_command = Command('parent')
        parent_context = Context(parent_command, info_name='parent')
        
        # Create a sub-command
        sub_command = Command('sub')
        
        # Create sub-context using _make_sub_context
        sub_context = parent_context._make_sub_context(sub_command)
        
        # Verify the sub-context is of the same type as parent
        assert type(sub_context) == type(parent_context)
        
        # Verify the sub-context has the correct command
        assert sub_context.command == sub_command
        
        # Verify the sub-context has the correct info_name
        assert sub_context.info_name == 'sub'
        
        # Verify the sub-context has the correct parent
        assert sub_context.parent == parent_context
    
    def test_make_sub_context_with_custom_context_class(self):
        """Test that _make_sub_context works with custom context classes"""
        
        # Create a custom context class
        class CustomContext(Context):
            custom_attr = "custom_value"
        
        # Create a parent context with custom class
        parent_command = Command('parent')
        parent_context = CustomContext(parent_command, info_name='parent')
        
        # Create a sub-command
        sub_command = Command('sub')
        
        # Create sub-context using _make_sub_context
        sub_context = parent_context._make_sub_context(sub_command)
        
        # Verify the sub-context is of the custom type
        assert type(sub_context) == CustomContext
        
        # Verify the sub-context has the custom attribute
        assert hasattr(sub_context, 'custom_attr')
        assert sub_context.custom_attr == "custom_value"
        
        # Verify the sub-context has the correct command
        assert sub_context.command == sub_command
        
        # Verify the sub-context has the correct info_name
        assert sub_context.info_name == 'sub'
        
        # Verify the sub-context has the correct parent
        assert sub_context.parent == parent_context
