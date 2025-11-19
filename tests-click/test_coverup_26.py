# file: src/click/src/click/_compat.py:452-485
# asked: {"lines": [452, 453, 454, 455, 456, 457, 459, 460, 461, 463, 464, 465, 466, 467, 468, 470, 471, 473, 474, 476, 482, 484, 485], "branches": [[464, 465], [464, 466]]}
# gained: {"lines": [452, 453, 454, 455, 456, 457, 459, 460, 461, 463, 464, 465, 466, 467, 468, 470, 471, 473, 474, 476, 482, 484, 485], "branches": [[464, 465], [464, 466]]}

import os
import tempfile
import pytest
from click._compat import _AtomicFile
from unittest.mock import mock_open, patch, MagicMock


class TestAtomicFile:
    def test_init_and_properties(self):
        """Test _AtomicFile initialization and property access."""
        mock_file = mock_open()()
        tmp_filename = "/tmp/temp.txt"
        real_filename = "/tmp/real.txt"
        
        atomic_file = _AtomicFile(mock_file, tmp_filename, real_filename)
        
        assert atomic_file._f == mock_file
        assert atomic_file._tmp_filename == tmp_filename
        assert atomic_file._real_filename == real_filename
        assert atomic_file.closed is False
        assert atomic_file.name == real_filename

    def test_close_normal(self, tmp_path):
        """Test normal close operation without delete."""
        tmp_file = tmp_path / "temp.txt"
        real_file = tmp_path / "real.txt"
        
        # Create temporary file with content
        with open(tmp_file, 'w') as f:
            f.write("test content")
        
        mock_file = mock_open()()
        atomic_file = _AtomicFile(mock_file, str(tmp_file), str(real_file))
        
        atomic_file.close(delete=False)
        
        assert atomic_file.closed is True
        assert real_file.exists()
        assert not tmp_file.exists()
        mock_file.close.assert_called_once()

    def test_close_already_closed(self):
        """Test close when file is already closed."""
        mock_file = mock_open()()
        atomic_file = _AtomicFile(mock_file, "/tmp/temp.txt", "/tmp/real.txt")
        atomic_file.closed = True
        
        atomic_file.close()
        
        # Should not call file operations when already closed
        mock_file.close.assert_not_called()

    def test_close_with_delete(self, tmp_path):
        """Test close operation with delete=True."""
        tmp_file = tmp_path / "temp.txt"
        real_file = tmp_path / "real.txt"
        
        # Create temporary file with content
        with open(tmp_file, 'w') as f:
            f.write("test content")
        
        mock_file = mock_open()()
        atomic_file = _AtomicFile(mock_file, str(tmp_file), str(real_file))
        
        atomic_file.close(delete=True)
        
        assert atomic_file.closed is True
        assert real_file.exists()
        assert not tmp_file.exists()
        mock_file.close.assert_called_once()

    def test_getattr_delegation(self):
        """Test attribute delegation to underlying file object."""
        mock_file = mock_open()()
        mock_file.read.return_value = "delegated content"
        
        atomic_file = _AtomicFile(mock_file, "/tmp/temp.txt", "/tmp/real.txt")
        
        # Test delegated method call
        result = atomic_file.read()
        assert result == "delegated content"
        mock_file.read.assert_called_once()
        
        # Test delegated attribute access
        mock_file.mode = "w"
        assert atomic_file.mode == "w"

    def test_context_manager_normal_exit(self, tmp_path):
        """Test context manager with normal exit (no exception)."""
        tmp_file = tmp_path / "temp.txt"
        real_file = tmp_path / "real.txt"
        
        # Create temporary file with content
        with open(tmp_file, 'w') as f:
            f.write("test content")
        
        mock_file = mock_open()()
        
        with _AtomicFile(mock_file, str(tmp_file), str(real_file)) as atomic_file:
            assert atomic_file.closed is False
        
        # After context manager exit, file should be closed and moved
        assert atomic_file.closed is True
        assert real_file.exists()
        assert not tmp_file.exists()
        mock_file.close.assert_called_once()

    def test_context_manager_with_exception(self, tmp_path):
        """Test context manager when exception occurs."""
        tmp_file = tmp_path / "temp.txt"
        real_file = tmp_path / "real.txt"
        
        # Create temporary file with content
        with open(tmp_file, 'w') as f:
            f.write("test content")
        
        mock_file = mock_open()()
        atomic_file = _AtomicFile(mock_file, str(tmp_file), str(real_file))
        
        # Simulate exception in context manager
        try:
            with atomic_file:
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # File should still be closed and moved even with exception
        assert atomic_file.closed is True
        assert real_file.exists()
        assert not tmp_file.exists()
        mock_file.close.assert_called_once()

    def test_repr(self):
        """Test __repr__ method."""
        mock_file = mock_open()()
        mock_file.__repr__ = MagicMock(return_value="<mock_file object>")
        
        atomic_file = _AtomicFile(mock_file, "/tmp/temp.txt", "/tmp/real.txt")
        
        repr_str = repr(atomic_file)
        assert repr_str == "<mock_file object>"
        mock_file.__repr__.assert_called_once()
