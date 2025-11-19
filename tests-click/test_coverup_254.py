# file: src/click/src/click/core.py:476-479
# asked: {"lines": [476, 477, 478, 479], "branches": []}
# gained: {"lines": [476, 477, 478, 479], "branches": []}

import pytest
import click
from click.core import Context
from click.globals import _local

class TestContextEnter:
    def test_context_enter_method(self):
        """Test that __enter__ method executes all lines and increases depth."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context
        ctx = Context(mock_command)
        
        # Store initial depth
        initial_depth = ctx._depth
        
        # Enter the context
        with ctx:
            # Verify depth increased by 1
            assert ctx._depth == initial_depth + 1
            
            # Verify context was pushed to the stack
            assert _local.stack is not None
            assert len(_local.stack) > 0
            assert _local.stack[-1] is ctx
            
            # Verify the context manager returns self
            assert ctx is ctx.__enter__()
        
        # Clean up - ensure stack is restored
        if hasattr(_local, 'stack'):
            while _local.stack and _local.stack[-1] is ctx:
                _local.stack.pop()

    def test_context_enter_multiple_times(self):
        """Test that __enter__ can be called multiple times and depth increases each time."""
        mock_command = click.Command('test_command')
        ctx = Context(mock_command)
        
        initial_depth = ctx._depth
        
        # Enter first time
        with ctx:
            assert ctx._depth == initial_depth + 1
            first_stack_size = len(_local.stack) if hasattr(_local, 'stack') else 0
            
            # Enter second time (nested)
            with ctx:
                assert ctx._depth == initial_depth + 2
                second_stack_size = len(_local.stack) if hasattr(_local, 'stack') else 0
                assert second_stack_size > first_stack_size
            
            # After first exit, depth should decrease
            assert ctx._depth == initial_depth + 1
        
        # After second exit, depth should be back to initial
        assert ctx._depth == initial_depth
        
        # Clean up
        if hasattr(_local, 'stack'):
            while _local.stack and _local.stack[-1] is ctx:
                _local.stack.pop()
