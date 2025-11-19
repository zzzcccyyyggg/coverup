# file: src/click/src/click/_compat.py:337-341
# asked: {"lines": [337, 338, 339, 340, 341], "branches": [[339, 340], [339, 341]]}
# gained: {"lines": [337, 338, 339, 340, 341], "branches": [[339, 340], [339, 341]]}

import pytest
import sys
import typing as t
from unittest.mock import Mock, patch
from click._compat import get_text_stdin


class TestGetTextStdin:
    def test_get_text_stdin_windows_console_stream_returns_none(self, monkeypatch):
        """Test when _get_windows_console_stream returns None, _force_correct_text_reader is called."""
        # Mock _get_windows_console_stream to return None
        monkeypatch.setattr('click._compat._get_windows_console_stream', lambda *args: None)
        
        # Mock _force_correct_text_reader to return a specific value
        mock_reader = Mock()
        monkeypatch.setattr('click._compat._force_correct_text_reader', lambda *args, **kwargs: mock_reader)
        
        result = get_text_stdin(encoding='utf-8', errors='strict')
        
        assert result is mock_reader

    def test_get_text_stdin_windows_console_stream_returns_stream(self, monkeypatch):
        """Test when _get_windows_console_stream returns a stream, it is returned directly."""
        # Mock _get_windows_console_stream to return a mock stream
        mock_stream = Mock()
        monkeypatch.setattr('click._compat._get_windows_console_stream', lambda *args: mock_stream)
        
        result = get_text_stdin(encoding='utf-8', errors='strict')
        
        assert result is mock_stream

    def test_get_text_stdin_with_none_encoding_and_errors(self, monkeypatch):
        """Test get_text_stdin with None encoding and errors."""
        # Mock _get_windows_console_stream to return None
        monkeypatch.setattr('click._compat._get_windows_console_stream', lambda *args: None)
        
        # Mock _force_correct_text_reader to return a specific value
        mock_reader = Mock()
        monkeypatch.setattr('click._compat._force_correct_text_reader', lambda *args, **kwargs: mock_reader)
        
        result = get_text_stdin(encoding=None, errors=None)
        
        assert result is mock_reader
