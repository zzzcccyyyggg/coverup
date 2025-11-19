# file: src/click/src/click/_compat.py:351-355
# asked: {"lines": [351, 352, 353, 354, 355], "branches": [[353, 354], [353, 355]]}
# gained: {"lines": [351, 352, 353, 354, 355], "branches": [[353, 354], [353, 355]]}

import pytest
import sys
import typing as t
from unittest.mock import Mock, patch
from click._compat import get_text_stderr


class TestGetTextStderr:
    def test_get_text_stderr_windows_console_returns_rv(self, monkeypatch):
        """Test that get_text_stderr returns _get_windows_console_stream result when not None"""
        mock_stream = Mock(spec=t.TextIO)
        
        with patch('click._compat._get_windows_console_stream', return_value=mock_stream):
            result = get_text_stderr(encoding='utf-16-le', errors='strict')
            
            assert result is mock_stream

    def test_get_text_stderr_windows_console_none_falls_back(self, monkeypatch):
        """Test that get_text_stderr falls back to _force_correct_text_writer when _get_windows_console_stream returns None"""
        mock_forced_stream = Mock(spec=t.TextIO)
        
        with patch('click._compat._get_windows_console_stream', return_value=None), \
             patch('click._compat._force_correct_text_writer', return_value=mock_forced_stream):
            result = get_text_stderr(encoding='utf-8', errors='replace')
            
            assert result is mock_forced_stream

    def test_get_text_stderr_default_params(self, monkeypatch):
        """Test get_text_stderr with default parameters"""
        mock_forced_stream = Mock(spec=t.TextIO)
        
        with patch('click._compat._get_windows_console_stream', return_value=None), \
             patch('click._compat._force_correct_text_writer', return_value=mock_forced_stream):
            result = get_text_stderr()
            
            assert result is mock_forced_stream
