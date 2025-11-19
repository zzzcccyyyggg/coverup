# file: src/click/src/click/core.py:575-602
# asked: {"lines": [575, 602], "branches": []}
# gained: {"lines": [575, 602], "branches": []}

import pytest
from contextlib import AbstractContextManager
from click.core import Context
from click import Command

class MockContextManager(AbstractContextManager):
    def __init__(self, return_value="test_resource"):
        self.return_value = return_value
        self.entered = False
        self.exited = False
    
    def __enter__(self):
        self.entered = True
        return self.return_value
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.exited = True
        return False

def test_context_with_resource():
    """Test that with_resource properly registers and manages context managers."""
    # Create a minimal command for the context
    cmd = Command("test_cmd")
    
    # Create context and test with_resource
    ctx = Context(cmd)
    
    # Create a mock context manager
    mock_cm = MockContextManager("test_value")
    
    # Use with_resource to register the context manager
    result = ctx.with_resource(mock_cm)
    
    # Verify the resource was entered and returned the correct value
    assert mock_cm.entered == True
    assert result == "test_value"
    assert mock_cm.exited == False  # Should not be exited yet
    
    # Clean up by closing the context
    ctx.close()
    
    # Verify the resource was properly exited when context was closed
    assert mock_cm.exited == True

def test_context_with_resource_multiple():
    """Test that with_resource works with multiple context managers."""
    cmd = Command("test_cmd")
    ctx = Context(cmd)
    
    # Create multiple mock context managers
    cm1 = MockContextManager("value1")
    cm2 = MockContextManager("value2")
    cm3 = MockContextManager("value3")
    
    # Register all of them
    result1 = ctx.with_resource(cm1)
    result2 = ctx.with_resource(cm2) 
    result3 = ctx.with_resource(cm3)
    
    # Verify all were entered and returned correct values
    assert result1 == "value1"
    assert result2 == "value2" 
    assert result3 == "value3"
    assert cm1.entered and cm2.entered and cm3.entered
    assert not any([cm1.exited, cm2.exited, cm3.exited])
    
    # Clean up
    ctx.close()
    
    # Verify all were properly exited
    assert all([cm1.exited, cm2.exited, cm3.exited])

def test_context_with_resource_nested():
    """Test that with_resource works correctly with nested contexts."""
    cmd = Command("test_cmd")
    parent_ctx = Context(cmd)
    
    # Create a mock context manager for parent
    parent_cm = MockContextManager("parent_value")
    parent_result = parent_ctx.with_resource(parent_cm)
    
    # Create child context
    child_ctx = Context(cmd, parent=parent_ctx, info_name="child")
    
    # Create a mock context manager for child
    child_cm = MockContextManager("child_value")
    child_result = child_ctx.with_resource(child_cm)
    
    # Verify both were entered
    assert parent_result == "parent_value"
    assert child_result == "child_value"
    assert parent_cm.entered and child_cm.entered
    assert not parent_cm.exited and not child_cm.exited
    
    # Close child context first
    child_ctx.close()
    assert child_cm.exited == True
    assert parent_cm.exited == False  # Parent should still be active
    
    # Close parent context
    parent_ctx.close()
    assert parent_cm.exited == True

def test_context_with_resource_exception_handling():
    """Test that with_resource properly handles exceptions in context managers."""
    class ExceptionContextManager(AbstractContextManager):
        def __init__(self, raise_on_enter=False, raise_on_exit=False):
            self.raise_on_enter = raise_on_enter
            self.raise_on_exit = raise_on_exit
            self.entered = False
            self.exited = False
        
        def __enter__(self):
            self.entered = True
            if self.raise_on_enter:
                raise RuntimeError("Enter failed")
            return "test_value"
        
        def __exit__(self, exc_type, exc_value, traceback):
            self.exited = True
            if self.raise_on_exit:
                raise RuntimeError("Exit failed")
            return False
    
    cmd = Command("test_cmd")
    ctx = Context(cmd)
    
    # Test normal context manager
    normal_cm = ExceptionContextManager()
    result = ctx.with_resource(normal_cm)
    assert result == "test_value"
    assert normal_cm.entered == True
    
    # Clean up
    ctx.close()
    assert normal_cm.exited == True
    
    # Test context manager that raises on enter
    ctx2 = Context(cmd)
    failing_cm = ExceptionContextManager(raise_on_enter=True)
    
    with pytest.raises(RuntimeError, match="Enter failed"):
        ctx2.with_resource(failing_cm)
    
    # Clean up
    ctx2.close()
