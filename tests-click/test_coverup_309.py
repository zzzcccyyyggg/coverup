# file: src/click/src/click/core.py:616-621
# asked: {"lines": [616, 621], "branches": []}
# gained: {"lines": [616, 621], "branches": []}

import pytest
from click.core import Context
from click import Command

def test_context_close():
    """Test that Context.close() calls _close_with_exception_info with None arguments."""
    # Create a minimal command to instantiate Context
    cmd = Command('test_cmd')
    ctx = Context(cmd)
    
    # Mock _close_with_exception_info to verify it's called with correct arguments
    called_with = []
    original_method = ctx._close_with_exception_info
    
    def mock_close(exc_type, exc_value, tb):
        called_with.append((exc_type, exc_value, tb))
        return original_method(exc_type, exc_value, tb)
    
    ctx._close_with_exception_info = mock_close
    
    # Call close method
    ctx.close()
    
    # Verify _close_with_exception_info was called with None arguments
    assert len(called_with) == 1
    assert called_with[0] == (None, None, None)
