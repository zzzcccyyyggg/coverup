# file: src/click/src/click/_compat.py:559-560
# asked: {"lines": [559, 560], "branches": []}
# gained: {"lines": [559, 560], "branches": []}

import pytest
import sys
from click._compat import _get_argv_encoding

class TestGetArgvEncoding:
    def test_get_argv_encoding_with_stdin_encoding(self, monkeypatch):
        # Mock sys.stdin to have an encoding attribute
        mock_stdin = type('MockStdin', (), {'encoding': 'utf-8'})()
        monkeypatch.setattr(sys, 'stdin', mock_stdin)
        
        result = _get_argv_encoding()
        assert result == 'utf-8'

    def test_get_argv_encoding_without_stdin_encoding(self, monkeypatch):
        # Mock sys.stdin to not have an encoding attribute
        mock_stdin = type('MockStdin', (), {})()
        monkeypatch.setattr(sys, 'stdin', mock_stdin)
        
        # Mock sys.getfilesystemencoding to return a known value
        monkeypatch.setattr(sys, 'getfilesystemencoding', lambda: 'ascii')
        
        result = _get_argv_encoding()
        assert result == 'ascii'

    def test_get_argv_encoding_with_none_stdin_encoding(self, monkeypatch):
        # Mock sys.stdin to have encoding=None
        mock_stdin = type('MockStdin', (), {'encoding': None})()
        monkeypatch.setattr(sys, 'stdin', mock_stdin)
        
        # Mock sys.getfilesystemencoding to return a known value
        monkeypatch.setattr(sys, 'getfilesystemencoding', lambda: 'ascii')
        
        result = _get_argv_encoding()
        assert result == 'ascii'
