# file: src/click/src/click/globals.py:20-41
# asked: {"lines": [20, 35, 36, 37, 38, 39, 41], "branches": [[38, 39], [38, 41]]}
# gained: {"lines": [20, 35, 36, 37, 38, 39, 41], "branches": [[38, 39], [38, 41]]}

import pytest
import typing as t
from click.core import Context, Command
from click.globals import get_current_context, _local


class MockCommand(Command):
    """A mock command for testing purposes."""
    def __init__(self, name="test_command"):
        super().__init__(name=name)


class TestGetCurrentContext:
    def test_get_current_context_with_active_context(self):
        """Test that get_current_context returns the top context when stack has items."""
        # Setup: create a mock context and push it to the stack
        mock_command = MockCommand()
        mock_context = Context(mock_command)
        if not hasattr(_local, 'stack'):
            _local.stack = []
        _local.stack.append(mock_context)
        
        try:
            # Execute
            result = get_current_context()
            
            # Assert
            assert result is mock_context
        finally:
            # Cleanup: pop the context from stack
            if _local.stack:
                _local.stack.pop()

    def test_get_current_context_no_context_raises_runtime_error(self):
        """Test that get_current_context raises RuntimeError when no context and silent=False."""
        # Setup: ensure stack is empty or non-existent
        if hasattr(_local, 'stack'):
            original_stack = _local.stack
            _local.stack = []
        else:
            original_stack = None
        
        try:
            # Execute and assert
            with pytest.raises(RuntimeError, match="There is no active click context."):
                get_current_context(silent=False)
        finally:
            # Cleanup: restore original stack state
            if original_stack is not None:
                _local.stack = original_stack
            elif hasattr(_local, 'stack'):
                delattr(_local, 'stack')

    def test_get_current_context_no_context_silent_returns_none(self):
        """Test that get_current_context returns None when no context and silent=True."""
        # Setup: ensure stack is empty or non-existent
        if hasattr(_local, 'stack'):
            original_stack = _local.stack
            _local.stack = []
        else:
            original_stack = None
        
        try:
            # Execute
            result = get_current_context(silent=True)
            
            # Assert
            assert result is None
        finally:
            # Cleanup: restore original stack state
            if original_stack is not None:
                _local.stack = original_stack
            elif hasattr(_local, 'stack'):
                delattr(_local, 'stack')

    def test_get_current_context_no_stack_attribute_raises_runtime_error(self):
        """Test that get_current_context raises RuntimeError when _local has no stack attribute."""
        # Setup: remove stack attribute if it exists
        if hasattr(_local, 'stack'):
            original_stack = _local.stack
            delattr(_local, 'stack')
        else:
            original_stack = None
        
        try:
            # Execute and assert
            with pytest.raises(RuntimeError, match="There is no active click context."):
                get_current_context(silent=False)
        finally:
            # Cleanup: restore original stack state
            if original_stack is not None:
                _local.stack = original_stack

    def test_get_current_context_no_stack_attribute_silent_returns_none(self):
        """Test that get_current_context returns None when _local has no stack attribute and silent=True."""
        # Setup: remove stack attribute if it exists
        if hasattr(_local, 'stack'):
            original_stack = _local.stack
            delattr(_local, 'stack')
        else:
            original_stack = None
        
        try:
            # Execute
            result = get_current_context(silent=True)
            
            # Assert
            assert result is None
        finally:
            # Cleanup: restore original stack state
            if original_stack is not None:
                _local.stack = original_stack
