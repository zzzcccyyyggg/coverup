# file: src/click/src/click/utils.py:407-446
# asked: {"lines": [407, 409, 434, 435, 437, 439, 440, 442, 443, 446], "branches": [[434, 435], [434, 437], [439, 440], [439, 442]]}
# gained: {"lines": [407, 409, 434, 435, 437, 439, 440, 442, 443, 446], "branches": [[434, 435], [434, 437], [439, 440], [439, 442]]}

import pytest
import os
import sys
from click.utils import format_filename

class TestFormatFilename:
    def test_format_filename_bytes_with_surrogate_escape(self):
        """Test that bytes with surrogate escapes are properly handled."""
        # Create bytes that would contain surrogate escapes when decoded
        filename_bytes = b'test\xed\xa0\x80file.txt'  # Contains surrogate pair
        result = format_filename(filename_bytes)
        assert isinstance(result, str)
        # Should contain replacement character for invalid bytes
        assert '�' in result

    def test_format_filename_bytes_invalid_encoding(self):
        """Test that bytes with invalid encoding are handled with replacement."""
        # Create bytes with invalid encoding for filesystem encoding
        invalid_bytes = b'test\xff\xfffile.txt'  # Invalid bytes
        result = format_filename(invalid_bytes)
        assert isinstance(result, str)
        # Should contain replacement character for invalid bytes
        assert '�' in result

    def test_format_filename_str_with_surrogate_escape(self):
        """Test that string with surrogate escapes are properly handled."""
        # Create a string with surrogate escapes using surrogateescape encoding
        # First create bytes with surrogate escapes, then decode with surrogateescape
        filename_bytes = b'test\xed\xa0\x80file.txt'
        filename_str = filename_bytes.decode('utf-8', 'surrogateescape')
        result = format_filename(filename_str)
        assert isinstance(result, str)
        # The surrogate should be replaced with replacement character
        assert '�' in result

    def test_format_filename_pathlike_with_surrogate_escape(self):
        """Test that PathLike objects with surrogate escapes are handled."""
        # Create bytes with surrogate escapes, then decode with surrogateescape
        filename_bytes = b'test\xed\xa0\x80path.txt'
        filename_str = filename_bytes.decode('utf-8', 'surrogateescape')
        
        class CustomPath:
            def __fspath__(self):
                return filename_str
        
        path_obj = CustomPath()
        result = format_filename(path_obj)
        assert isinstance(result, str)
        assert '�' in result

    def test_format_filename_shorten_bytes(self):
        """Test shorten=True with bytes input."""
        filename_bytes = b'/path/to/test\xed\xa0\x80file.txt'
        result = format_filename(filename_bytes, shorten=True)
        assert isinstance(result, str)
        assert '�' in result
        # Should only contain the basename, not the full path
        assert 'path' not in result
        assert 'to' not in result

    def test_format_filename_shorten_str_with_surrogate(self):
        """Test shorten=True with string containing surrogate escapes."""
        # Create bytes with surrogate escapes, then decode with surrogateescape
        filename_bytes = b'/path/to/test\xed\xa0\x80file.txt'
        filename_str = filename_bytes.decode('utf-8', 'surrogateescape')
        result = format_filename(filename_str, shorten=True)
        assert isinstance(result, str)
        assert '�' in result
        # Should only contain the basename, not the full path
        assert 'path' not in result
        assert 'to' not in result

    def test_format_filename_pathlike_shorten(self):
        """Test shorten=True with PathLike object."""
        # Create bytes with surrogate escapes, then decode with surrogateescape
        filename_bytes = b'/path/to/test\xed\xa0\x80file.txt'
        filename_str = filename_bytes.decode('utf-8', 'surrogateescape')
        
        class CustomPath:
            def __fspath__(self):
                return filename_str
        
        path_obj = CustomPath()
        result = format_filename(path_obj, shorten=True)
        assert isinstance(result, str)
        assert '�' in result
        # Should only contain the basename, not the full path
        assert 'path' not in result
        assert 'to' not in result

    def test_format_filename_valid_bytes(self):
        """Test valid bytes that decode properly."""
        valid_bytes = b'test_file.txt'
        result = format_filename(valid_bytes)
        assert result == 'test_file.txt'

    def test_format_filename_valid_str(self):
        """Test valid string without surrogate escapes."""
        valid_str = 'test_file.txt'
        result = format_filename(valid_str)
        assert result == 'test_file.txt'

    def test_format_filename_valid_pathlike(self):
        """Test valid PathLike object."""
        class CustomPath:
            def __fspath__(self):
                return 'test_file.txt'
        
        path_obj = CustomPath()
        result = format_filename(path_obj)
        assert result == 'test_file.txt'

    def test_format_filename_shorten_valid_str(self):
        """Test shorten=True with valid string."""
        valid_str = '/path/to/test_file.txt'
        result = format_filename(valid_str, shorten=True)
        assert result == 'test_file.txt'

    def test_format_filename_shorten_valid_pathlike(self):
        """Test shorten=True with valid PathLike object."""
        class CustomPath:
            def __fspath__(self):
                return '/path/to/test_file.txt'
        
        path_obj = CustomPath()
        result = format_filename(path_obj, shorten=True)
        assert result == 'test_file.txt'
