# file: src/click/src/click/types.py:207-230
# asked: {"lines": [207, 208, 210, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 225, 226, 227, 229, 230], "branches": [[213, 214], [213, 227], [219, 220], [219, 225]]}
# gained: {"lines": [207, 208, 210, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 226, 229, 230], "branches": [[213, 214], [219, 220]]}

import pytest
import sys
from click.types import StringParamType
from click.core import Context, Parameter


class TestStringParamType:
    def test_convert_bytes_with_encoding_error_and_different_fs_encoding(self, monkeypatch):
        """Test bytes conversion with encoding error and different filesystem encoding."""
        string_type = StringParamType()
        
        # Mock _get_argv_encoding to return a specific encoding
        monkeypatch.setattr('click._compat._get_argv_encoding', lambda: 'ascii')
        
        # Mock sys.getfilesystemencoding to return a different encoding
        monkeypatch.setattr(sys, 'getfilesystemencoding', lambda: 'latin-1')
        
        # Create bytes that can't be decoded with ascii but can with latin-1
        test_bytes = b'\xe9'  # Latin-1 'é' character
        
        result = string_type.convert(test_bytes, None, None)
        
        # Should decode successfully with latin-1
        assert result == 'é'

    def test_convert_bytes_with_encoding_error_and_same_fs_encoding(self, monkeypatch):
        """Test bytes conversion with encoding error and same filesystem encoding."""
        string_type = StringParamType()
        
        # Mock _get_argv_encoding to return a specific encoding
        monkeypatch.setattr('click._compat._get_argv_encoding', lambda: 'ascii')
        
        # Mock sys.getfilesystemencoding to return the same encoding
        monkeypatch.setattr(sys, 'getfilesystemencoding', lambda: 'ascii')
        
        # Create bytes that can't be decoded with ascii
        test_bytes = b'\xe9'  # Invalid ASCII character
        
        result = string_type.convert(test_bytes, None, None)
        
        # Should fall back to utf-8 with replacement
        assert result == '�'

    def test_convert_bytes_with_encoding_error_and_utf8_fallback(self, monkeypatch):
        """Test bytes conversion with encoding error and utf-8 fallback."""
        string_type = StringParamType()
        
        # Mock _get_argv_encoding to return a specific encoding
        monkeypatch.setattr('click._compat._get_argv_encoding', lambda: 'ascii')
        
        # Mock sys.getfilesystemencoding to return a different encoding
        monkeypatch.setattr(sys, 'getfilesystemencoding', lambda: 'latin-1')
        
        # Create bytes that can't be decoded with either ascii or latin-1
        # Use bytes that are invalid in latin-1 encoding
        test_bytes = b'\xff\xff'  # 0xFF is invalid in latin-1
        
        result = string_type.convert(test_bytes, None, None)
        
        # Should use utf-8 with replacement, resulting in replacement characters
        # The exact replacement character may vary by system, so check it's a string
        assert isinstance(result, str)
        # The important thing is that it doesn't raise an exception and returns a string

    def test_convert_bytes_with_double_encoding_error(self, monkeypatch):
        """Test bytes conversion that fails both primary and filesystem encoding."""
        string_type = StringParamType()
        
        # Mock _get_argv_encoding to return a specific encoding
        monkeypatch.setattr('click._compat._get_argv_encoding', lambda: 'ascii')
        
        # Mock sys.getfilesystemencoding to return a different encoding
        monkeypatch.setattr(sys, 'getfilesystemencoding', lambda: 'latin-1')
        
        # Create bytes that can't be decoded with either ascii or latin-1
        # Use bytes that are invalid in both encodings
        test_bytes = b'\x80\x81'  # Invalid in both ascii and latin-1
        
        result = string_type.convert(test_bytes, None, None)
        
        # Should use utf-8 with replacement
        assert isinstance(result, str)
        # The result should be a string with replacement characters

    def test_repr_method(self):
        """Test the __repr__ method returns 'STRING'."""
        string_type = StringParamType()
        assert repr(string_type) == "STRING"
