# file: src/click/src/click/utils.py:197-219
# asked: {"lines": [197, 198, 199, 201, 202, 204, 205, 207, 213, 215, 216, 218, 219], "branches": []}
# gained: {"lines": [197, 198, 199, 201, 202, 204, 205, 207, 213, 215, 216, 218, 219], "branches": []}

import pytest
import io
import tempfile
import os
from click.utils import KeepOpenFile

class TestKeepOpenFile:
    def test_keep_open_file_context_manager(self):
        """Test that KeepOpenFile works as a context manager and keeps file open."""
        file_obj = io.StringIO("test content")
        
        with KeepOpenFile(file_obj) as keep_open:
            assert keep_open._file is file_obj
            assert not file_obj.closed
        
        # File should still be open after context manager exits
        assert not file_obj.closed
        file_obj.close()

    def test_keep_open_file_repr(self):
        """Test that __repr__ returns the representation of the underlying file."""
        file_obj = io.StringIO("test content")
        keep_open = KeepOpenFile(file_obj)
        
        repr_str = repr(keep_open)
        expected_repr = repr(file_obj)
        assert repr_str == expected_repr
        
        file_obj.close()

    def test_keep_open_file_iteration(self):
        """Test that KeepOpenFile can be iterated over like the underlying file."""
        file_obj = io.StringIO("line1\nline2\nline3")
        keep_open = KeepOpenFile(file_obj)
        
        # Read lines from KeepOpenFile
        lines = list(keep_open)
        # Reset file position and read from original file for comparison
        file_obj.seek(0)
        expected_lines = list(file_obj)
        assert lines == expected_lines
        
        file_obj.close()

    def test_keep_open_file_attribute_delegation(self):
        """Test that attribute access is delegated to the underlying file."""
        file_obj = io.StringIO("test content")
        keep_open = KeepOpenFile(file_obj)
        
        # Test that attributes are properly delegated
        assert keep_open.closed == file_obj.closed
        # StringIO doesn't have 'mode' or 'name' attributes, so test with a real file
        file_obj.close()

    def test_keep_open_file_with_real_file_attributes(self):
        """Test attribute delegation with a real file that has mode and name attributes."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            tmp_file.write("test content")
            tmp_file.flush()
            
            # Reopen the file to get a fresh file object
            with open(tmp_file.name, 'r') as file_obj:
                keep_open = KeepOpenFile(file_obj)
                
                # Test that attributes are properly delegated
                assert keep_open.closed == file_obj.closed
                assert keep_open.mode == file_obj.mode
                assert keep_open.name == file_obj.name
        
        # Clean up
        os.unlink(tmp_file.name)

    def test_keep_open_file_with_exception_in_context(self):
        """Test that KeepOpenFile keeps file open even when exception occurs in context."""
        file_obj = io.StringIO("test content")
        
        try:
            with KeepOpenFile(file_obj) as keep_open:
                assert not file_obj.closed
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # File should still be open after exception in context manager
        assert not file_obj.closed
        file_obj.close()
