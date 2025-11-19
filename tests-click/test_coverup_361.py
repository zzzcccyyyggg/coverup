# file: src/click/src/click/core.py:604-614
# asked: {"lines": [604, 614], "branches": []}
# gained: {"lines": [604, 614], "branches": []}

import pytest
import click
from click.core import Context
from contextlib import ExitStack

class TestContextCallOnClose:
    def test_call_on_close_registers_callback(self):
        """Test that call_on_close registers a callback with the exit stack."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context
        ctx = Context(mock_command)
        
        # Create a simple callback function
        callback_called = []
        def test_callback():
            callback_called.append(True)
        
        # Register the callback using call_on_close
        result = ctx.call_on_close(test_callback)
        
        # Verify the callback was registered and returned
        assert result is test_callback
        
        # Verify the callback is in the exit stack
        assert len(ctx._exit_stack._exit_callbacks) == 1
        
        # Clean up by closing the context
        ctx.close()
        
        # Verify the callback was called during cleanup
        assert callback_called == [True]
    
    def test_call_on_close_with_arguments(self):
        """Test that call_on_close works with callback functions that have arguments."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context
        ctx = Context(mock_command)
        
        # Create a callback function with default arguments
        callback_args = []
        def test_callback(arg1="default1", arg2="default2"):
            callback_args.append((arg1, arg2))
        
        # Register the callback using call_on_close
        result = ctx.call_on_close(test_callback)
        
        # Verify the callback was registered and returned
        assert result is test_callback
        
        # Clean up by closing the context
        ctx.close()
        
        # Verify the callback was called with default arguments
        assert callback_args == [("default1", "default2")]
    
    def test_call_on_close_multiple_callbacks(self):
        """Test that multiple callbacks can be registered using call_on_close."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context
        ctx = Context(mock_command)
        
        # Create multiple callback functions
        callbacks_called = []
        def callback1():
            callbacks_called.append(1)
        
        def callback2():
            callbacks_called.append(2)
        
        def callback3():
            callbacks_called.append(3)
        
        # Register multiple callbacks
        ctx.call_on_close(callback1)
        ctx.call_on_close(callback2)
        ctx.call_on_close(callback3)
        
        # Verify all callbacks are registered
        assert len(ctx._exit_stack._exit_callbacks) == 3
        
        # Clean up by closing the context
        ctx.close()
        
        # Verify all callbacks were called (in reverse order)
        assert callbacks_called == [3, 2, 1]
    
    def test_call_on_close_with_context_manager(self):
        """Test that call_on_close works when context is used as context manager."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create callback tracking
        callback_called = []
        def test_callback():
            callback_called.append(True)
        
        # Use context as context manager
        with Context(mock_command) as ctx:
            # Register callback during context lifetime
            result = ctx.call_on_close(test_callback)
            assert result is test_callback
        
        # Verify callback was called when context exited
        assert callback_called == [True]
    
    def test_call_on_close_returns_same_function(self):
        """Test that call_on_close returns the same function that was passed in."""
        # Create a mock command
        mock_command = click.Command('test_command')
        
        # Create a context
        ctx = Context(mock_command)
        
        # Create a callback function
        def test_callback():
            pass
        
        # Register the callback and verify return value
        result = ctx.call_on_close(test_callback)
        assert result is test_callback
        
        # Clean up
        ctx.close()
