# file: src/click/src/click/core.py:623-639
# asked: {"lines": [623, 635, 637, 639], "branches": []}
# gained: {"lines": [623, 635, 637, 639], "branches": []}

import pytest
from click.core import Context
from click import Command
from types import TracebackType
from contextlib import ExitStack
from unittest.mock import Mock, MagicMock, create_autospec


class TestContextCloseWithExceptionInfo:
    """Test cases for Context._close_with_exception_info method."""
    
    def test_close_with_exception_info_successful_exit(self):
        """Test _close_with_exception_info when ExitStack.__exit__ returns None (successful exit)."""
        # Create a mock command
        mock_command = Mock(spec=Command)
        
        # Create context with mocked exit stack
        ctx = Context(command=mock_command, info_name="test")
        
        # Mock the exit stack to return None (successful exit)
        mock_exit_stack = Mock()
        mock_exit_stack.__exit__ = Mock(return_value=None)
        ctx._exit_stack = mock_exit_stack
        
        # Call the method with exception info
        result = ctx._close_with_exception_info(
            exc_type=ValueError,
            exc_value=ValueError("test error"),
            tb=None
        )
        
        # Verify exit stack was called with correct parameters
        mock_exit_stack.__exit__.assert_called_once()
        call_args = mock_exit_stack.__exit__.call_args[0]
        assert call_args[0] is ValueError
        assert isinstance(call_args[1], ValueError)
        assert call_args[1].args == ("test error",)
        assert call_args[2] is None
        
        # Verify exit stack was replaced with a new one
        assert isinstance(ctx._exit_stack, ExitStack)
        assert ctx._exit_stack is not mock_exit_stack
        
        # Verify return value
        assert result is None
    
    def test_close_with_exception_info_with_traceback(self):
        """Test _close_with_exception_info with a traceback object."""
        # Create a mock command
        mock_command = Mock(spec=Command)
        
        # Create context with mocked exit stack
        ctx = Context(command=mock_command, info_name="test")
        
        # Mock the exit stack to return True (exception handled)
        mock_exit_stack = Mock()
        mock_exit_stack.__exit__ = Mock(return_value=True)
        ctx._exit_stack = mock_exit_stack
        
        # Create a mock traceback
        mock_tb = Mock(spec=TracebackType)
        
        # Call the method with all exception info
        result = ctx._close_with_exception_info(
            exc_type=RuntimeError,
            exc_value=RuntimeError("runtime error"),
            tb=mock_tb
        )
        
        # Verify exit stack was called with correct parameters including traceback
        mock_exit_stack.__exit__.assert_called_once()
        call_args = mock_exit_stack.__exit__.call_args[0]
        assert call_args[0] is RuntimeError
        assert isinstance(call_args[1], RuntimeError)
        assert call_args[1].args == ("runtime error",)
        assert call_args[2] is mock_tb
        
        # Verify exit stack was replaced with a new one
        assert isinstance(ctx._exit_stack, ExitStack)
        assert ctx._exit_stack is not mock_exit_stack
        
        # Verify return value
        assert result is True
    
    def test_close_with_exception_info_no_exception(self):
        """Test _close_with_exception_info when no exception occurred (all None)."""
        # Create a mock command
        mock_command = Mock(spec=Command)
        
        # Create context with mocked exit stack
        ctx = Context(command=mock_command, info_name="test")
        
        # Mock the exit stack to return False (exception not handled)
        mock_exit_stack = Mock()
        mock_exit_stack.__exit__ = Mock(return_value=False)
        ctx._exit_stack = mock_exit_stack
        
        # Call the method with no exception info (normal exit)
        result = ctx._close_with_exception_info(
            exc_type=None,
            exc_value=None,
            tb=None
        )
        
        # Verify exit stack was called with None values
        mock_exit_stack.__exit__.assert_called_once_with(None, None, None)
        
        # Verify exit stack was replaced with a new one
        assert isinstance(ctx._exit_stack, ExitStack)
        assert ctx._exit_stack is not mock_exit_stack
        
        # Verify return value
        assert result is False
    
    def test_close_with_exception_info_reuses_context(self):
        """Test that _close_with_exception_info allows context reuse by creating new exit stack."""
        # Create a mock command
        mock_command = Mock(spec=Command)
        
        # Create context
        ctx = Context(command=mock_command, info_name="test")
        
        # Store original exit stack reference
        original_exit_stack = ctx._exit_stack
        
        # Call the method
        result = ctx._close_with_exception_info(None, None, None)
        
        # Verify a new exit stack was created (different object)
        assert isinstance(ctx._exit_stack, ExitStack)
        assert ctx._exit_stack is not original_exit_stack
        
        # Verify the method can be called again with the new exit stack
        second_result = ctx._close_with_exception_info(None, None, None)
        
        # Verify another new exit stack was created
        assert isinstance(ctx._exit_stack, ExitStack)
        assert ctx._exit_stack is not original_exit_stack
        
        # Both calls should return False (ExitStack.__exit__ returns False by default when no exception)
        assert result is False
        assert second_result is False
