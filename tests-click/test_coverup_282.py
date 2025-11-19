# file: src/click/src/click/core.py:730-738
# asked: {"lines": [730, 737, 738], "branches": []}
# gained: {"lines": [730, 737, 738], "branches": []}

import pytest
from click.core import Context
from click.exceptions import Exit

class MockCommand:
    def __init__(self):
        self.allow_extra_args = False
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False

def test_context_exit_calls_close_and_raises_exit():
    """Test that Context.exit() calls close() and raises Exit with correct code."""
    command = MockCommand()
    context = Context(command=command)
    
    # Mock the close method to track if it's called
    close_called = False
    def mock_close():
        nonlocal close_called
        close_called = True
    
    context.close = mock_close
    
    # Test that exit raises Exit with default code 0
    with pytest.raises(Exit) as exc_info:
        context.exit()
    
    assert close_called, "close() should be called before exiting"
    assert exc_info.value.exit_code == 0, "Exit should have code 0 by default"

def test_context_exit_with_custom_code():
    """Test that Context.exit() works with custom exit codes."""
    command = MockCommand()
    context = Context(command=command)
    
    # Mock the close method
    close_called = False
    def mock_close():
        nonlocal close_called
        close_called = True
    
    context.close = mock_close
    
    # Test with custom exit code
    with pytest.raises(Exit) as exc_info:
        context.exit(code=42)
    
    assert close_called, "close() should be called before exiting"
    assert exc_info.value.exit_code == 42, "Exit should have the specified code"

def test_context_exit_calls_real_close_method():
    """Test that Context.exit() calls the actual close() method implementation."""
    command = MockCommand()
    context = Context(command=command)
    
    # Track if close callbacks are executed
    close_callback_called = False
    def close_callback():
        nonlocal close_callback_called
        close_callback_called = True
    
    context.call_on_close(close_callback)
    
    # Test that exit calls the real close method which executes callbacks
    with pytest.raises(Exit) as exc_info:
        context.exit(code=1)
    
    assert close_callback_called, "close() should execute registered callbacks"
    assert exc_info.value.exit_code == 1, "Exit should have the specified code"
