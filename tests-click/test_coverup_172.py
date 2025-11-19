# file: src/click/src/click/_compat.py:323-327
# asked: {"lines": [323, 324, 325, 326, 327], "branches": [[325, 326], [325, 327]]}
# gained: {"lines": [323, 324, 325, 326, 327], "branches": [[325, 326], [325, 327]]}

import pytest
import sys
import typing as t
from unittest.mock import Mock, patch
from click._compat import get_binary_stdout, _find_binary_writer


class TestGetBinaryStdout:
    def test_get_binary_stdout_success(self, monkeypatch):
        """Test get_binary_stdout when _find_binary_writer returns a valid writer."""
        mock_writer = Mock()
        monkeypatch.setattr('click._compat._find_binary_writer', lambda x: mock_writer)
        
        result = get_binary_stdout()
        assert result is mock_writer

    def test_get_binary_stdout_raises_runtime_error(self, monkeypatch):
        """Test get_binary_stdout when _find_binary_writer returns None."""
        monkeypatch.setattr('click._compat._find_binary_writer', lambda x: None)
        
        with pytest.raises(RuntimeError, match="Was not able to determine binary stream for sys.stdout."):
            get_binary_stdout()
