# file: src/click/src/click/globals.py:44-46
# asked: {"lines": [44, 46], "branches": []}
# gained: {"lines": [44, 46], "branches": []}

import pytest
from click.core import Context, Command
from click.globals import push_context, _local

class TestPushContext:
    def test_push_context_initializes_stack_when_none_exists(self):
        """Test that push_context initializes the stack when it doesn't exist."""
        # Ensure no stack exists initially
        if hasattr(_local, 'stack'):
            delattr(_local, 'stack')
        
        # Create a mock command and context
        cmd = Command('test')
        ctx = Context(cmd)
        
        # Push the context - this should initialize the stack
        push_context(ctx)
        
        # Verify the stack was created and contains the context
        assert hasattr(_local, 'stack')
        assert _local.stack == [ctx]
        
        # Clean up
        delattr(_local, 'stack')
    
    def test_push_context_appends_to_existing_stack(self):
        """Test that push_context appends to an existing stack."""
        # Create mock commands and contexts
        cmd1 = Command('test1')
        cmd2 = Command('test2')
        existing_ctx = Context(cmd1)
        new_ctx = Context(cmd2)
        
        # Set up an existing stack with one context
        _local.stack = [existing_ctx]
        
        # Push the new context
        push_context(new_ctx)
        
        # Verify the stack contains both contexts
        assert _local.stack == [existing_ctx, new_ctx]
        
        # Clean up
        delattr(_local, 'stack')
