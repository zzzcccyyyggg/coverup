# file: src/click/src/click/_compat.py:330-334
# asked: {"lines": [330, 331, 332, 333, 334], "branches": [[332, 333], [332, 334]]}
# gained: {"lines": [330, 331, 332, 333, 334], "branches": [[332, 333], [332, 334]]}

import pytest
import sys
import typing as t
from unittest.mock import Mock, patch

def test_get_binary_stderr_raises_runtime_error(monkeypatch):
    """Test that get_binary_stderr raises RuntimeError when no binary writer can be found."""
    
    # Mock _find_binary_writer to return None, simulating no binary writer found
    monkeypatch.setattr('click._compat._find_binary_writer', lambda x: None)
    
    # Import the function after patching to ensure the mock is used
    from click._compat import get_binary_stderr
    
    # Verify that RuntimeError is raised with the expected message
    with pytest.raises(RuntimeError, match="Was not able to determine binary stream for sys.stderr."):
        get_binary_stderr()

def test_get_binary_stderr_returns_writer(monkeypatch):
    """Test that get_binary_stderr returns the binary writer when found."""
    
    # Create a mock binary writer
    mock_writer = Mock()
    
    # Mock _find_binary_writer to return our mock writer
    monkeypatch.setattr('click._compat._find_binary_writer', lambda x: mock_writer)
    
    # Import the function after patching to ensure the mock is used
    from click._compat import get_binary_stderr
    
    # Call the function and verify it returns our mock writer
    result = get_binary_stderr()
    assert result is mock_writer
