# file: src/click/src/click/_compat.py:344-348
# asked: {"lines": [344, 345, 346, 347, 348], "branches": [[346, 347], [346, 348]]}
# gained: {"lines": [344, 345, 346, 347, 348], "branches": [[346, 347], [346, 348]]}

import sys
import pytest
from unittest.mock import Mock, patch
from click._compat import get_text_stdout


class TestGetTextStdout:
    """Test cases for get_text_stdout function to achieve full coverage."""
    
    def test_get_text_stdout_windows_console_returns_rv(self, monkeypatch):
        """Test that get_text_stdout returns _get_windows_console_stream result when not None."""
        # Mock _get_windows_console_stream to return a mock TextIO object
        mock_stream = Mock(spec=sys.stdout)
        with patch('click._compat._get_windows_console_stream', return_value=mock_stream):
            result = get_text_stdout(encoding='utf-8', errors='strict')
            assert result is mock_stream
    
    def test_get_text_stdout_windows_console_returns_none_calls_force_correct_text_writer(self, monkeypatch):
        """Test that get_text_stdout calls _force_correct_text_writer when _get_windows_console_stream returns None."""
        # Mock _get_windows_console_stream to return None
        mock_forced_stream = Mock(spec=sys.stdout)
        with patch('click._compat._get_windows_console_stream', return_value=None), \
             patch('click._compat._force_correct_text_writer', return_value=mock_forced_stream) as mock_force:
            result = get_text_stdout(encoding='utf-8', errors='strict')
            mock_force.assert_called_once_with(sys.stdout, 'utf-8', 'strict', force_writable=True)
            assert result is mock_forced_stream
