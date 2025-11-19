# file: src/click/src/click/utils.py:143-144
# asked: {"lines": [143, 144], "branches": []}
# gained: {"lines": [143, 144], "branches": []}

import pytest
import tempfile
import os
from click.utils import LazyFile

class TestLazyFileGetAttr:
    def test_getattr_delegates_to_open_file(self, tmp_path):
        """Test that __getattr__ delegates to the opened file object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        
        lazy_file = LazyFile(str(test_file), mode='r')
        
        # Access an attribute that should be delegated to the underlying file
        # The 'name' attribute of the file object should be the file path
        assert lazy_file.name == str(test_file)
        
        # Clean up
        lazy_file.close()

    def test_getattr_with_nonexistent_attribute_raises_attribute_error(self, tmp_path):
        """Test that __getattr__ properly raises AttributeError for non-existent attributes."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        
        lazy_file = LazyFile(str(test_file), mode='r')
        
        # Try to access a non-existent attribute
        with pytest.raises(AttributeError):
            _ = lazy_file.nonexistent_attribute
        
        # Clean up
        lazy_file.close()

    def test_getattr_with_file_methods(self, tmp_path):
        """Test that __getattr__ properly delegates file methods."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        
        lazy_file = LazyFile(str(test_file), mode='r')
        
        # Access file methods through __getattr__
        read_method = lazy_file.read
        assert callable(read_method)
        
        # Actually call the method to verify it works
        content = read_method()
        assert content == "hello world"
        
        # Clean up
        lazy_file.close()

    def test_getattr_with_stdin(self, monkeypatch):
        """Test __getattr__ with stdin (special case where file is already open)."""
        import io
        import sys
        
        # Mock stdin to be a StringIO
        mock_stdin = io.StringIO("test input")
        monkeypatch.setattr(sys, 'stdin', mock_stdin)
        
        lazy_file = LazyFile('-', mode='r')
        
        # Access an attribute that should be delegated to the underlying file
        # For stdin, the 'mode' attribute should be accessible
        assert lazy_file.mode == 'r'
        
        # Clean up
        lazy_file.close()
