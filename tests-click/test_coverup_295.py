# file: src/click/src/click/types.py:875-876
# asked: {"lines": [875, 876], "branches": []}
# gained: {"lines": [875, 876], "branches": []}

import pytest
import typing as t
import typing_extensions as te
from click.types import _is_file_like


class TestFileLike:
    """Test cases for _is_file_like function."""
    
    def test_has_read_method(self):
        """Test that an object with read method is considered file-like."""
        class Readable:
            def read(self):
                pass
        
        obj = Readable()
        result = _is_file_like(obj)
        assert result is True
    
    def test_has_write_method(self):
        """Test that an object with write method is considered file-like."""
        class Writable:
            def write(self):
                pass
        
        obj = Writable()
        result = _is_file_like(obj)
        assert result is True
    
    def test_has_both_read_and_write_methods(self):
        """Test that an object with both read and write methods is considered file-like."""
        class ReadWritable:
            def read(self):
                pass
            def write(self):
                pass
        
        obj = ReadWritable()
        result = _is_file_like(obj)
        assert result is True
    
    def test_no_file_methods(self):
        """Test that an object without read or write methods is not considered file-like."""
        class NotFileLike:
            def some_other_method(self):
                pass
        
        obj = NotFileLike()
        result = _is_file_like(obj)
        assert result is False
    
    def test_none_value(self):
        """Test that None is not considered file-like."""
        result = _is_file_like(None)
        assert result is False
    
    def test_string_value(self):
        """Test that a string is not considered file-like."""
        result = _is_file_like("some string")
        assert result is False
    
    def test_integer_value(self):
        """Test that an integer is not considered file-like."""
        result = _is_file_like(42)
        assert result is False
