# file: src/click/src/click/_termui_impl.py:620-621
# asked: {"lines": [620, 621], "branches": []}
# gained: {"lines": [620, 621], "branches": []}

import pytest
import typing as t
from click._termui_impl import Editor
from unittest.mock import patch, MagicMock


class TestEditor:
    def test_edit_bytes_overload(self):
        """Test that the bytes/bytearray overload is properly defined."""
        editor = Editor()
        
        # Mock the edit_files method to avoid actual editor execution
        with patch.object(editor, 'edit_files') as mock_edit_files:
            # This should not raise any type errors and should match the overload
            result: bytes | None = editor.edit(b"test bytes")
            
            # Verify that edit_files was called with a filename
            mock_edit_files.assert_called_once()
            args, _ = mock_edit_files.call_args
            assert len(args) == 1
            assert isinstance(args[0], tuple)
            assert len(args[0]) == 1
            assert args[0][0].endswith('.txt')
            
            # Test with bytearray as well
            mock_edit_files.reset_mock()
            result: bytes | None = editor.edit(bytearray(b"test bytearray"))
            mock_edit_files.assert_called_once()
            args, _ = mock_edit_files.call_args
            assert len(args) == 1
            assert isinstance(args[0], tuple)
            assert len(args[0]) == 1
            assert args[0][0].endswith('.txt')
