# file: src/click/src/click/_compat.py:316-320
# asked: {"lines": [316, 317, 318, 319, 320], "branches": [[318, 319], [318, 320]]}
# gained: {"lines": [316, 317, 318, 319, 320], "branches": [[318, 319], [318, 320]]}

import pytest
import sys
import typing as t
from unittest.mock import Mock, patch
import io

def test_get_binary_stdin_success():
    """Test get_binary_stdin when sys.stdin is already a binary reader."""
    with patch('sys.stdin', io.BytesIO(b'test')):
        from click._compat import get_binary_stdin
        result = get_binary_stdin()
        assert isinstance(result, io.BytesIO)

def test_get_binary_stdin_with_buffer():
    """Test get_binary_stdin when sys.stdin has a binary buffer."""
    mock_stdin = Mock()
    mock_buffer = io.BytesIO(b'test')
    mock_stdin.buffer = mock_buffer
    with patch('sys.stdin', mock_stdin):
        from click._compat import get_binary_stdin
        result = get_binary_stdin()
        assert result is mock_buffer

def test_get_binary_stdin_raises_runtime_error():
    """Test get_binary_stdin raises RuntimeError when no binary reader can be found."""
    mock_stdin = Mock()
    mock_stdin.buffer = None
    with patch('sys.stdin', mock_stdin):
        from click._compat import get_binary_stdin
        with pytest.raises(RuntimeError, match="Was not able to determine binary stream for sys.stdin."):
            get_binary_stdin()
