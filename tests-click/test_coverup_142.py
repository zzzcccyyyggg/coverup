# file: src/click/src/click/utils.py:49-56
# asked: {"lines": [49, 51, 52, 53, 54, 55, 56], "branches": [[51, 52], [51, 56]]}
# gained: {"lines": [49, 51, 52, 53, 54, 55, 56], "branches": [[51, 52], [51, 56]]}

import pytest
import sys
import typing as t
from click.utils import make_str


class TestMakeStr:
    def test_make_str_with_bytes_valid_encoding(self):
        """Test make_str with bytes that can be decoded with filesystem encoding."""
        # Create bytes that can be decoded with filesystem encoding
        test_bytes = b"hello world"
        result = make_str(test_bytes)
        expected = test_bytes.decode(sys.getfilesystemencoding())
        assert result == expected
        assert isinstance(result, str)

    def test_make_str_with_bytes_unicode_error_fallback(self, monkeypatch):
        """Test make_str with bytes that cause UnicodeError and fallback to utf-8."""
        # Mock sys.getfilesystemencoding to return an encoding that will cause UnicodeError
        def mock_getfilesystemencoding():
            return 'ascii'
        
        monkeypatch.setattr(sys, 'getfilesystemencoding', mock_getfilesystemencoding)
        
        # Create bytes with non-ASCII characters that will fail with ASCII encoding
        test_bytes = b'hello \xff world'
        result = make_str(test_bytes)
        
        # Should fall back to utf-8 with replace
        expected = test_bytes.decode('utf-8', 'replace')
        assert result == expected
        assert isinstance(result, str)

    def test_make_str_with_non_bytes_value(self):
        """Test make_str with non-bytes values that go through str() conversion."""
        # Test with integer
        result = make_str(42)
        assert result == "42"
        assert isinstance(result, str)
        
        # Test with float
        result = make_str(3.14)
        assert result == "3.14"
        assert isinstance(result, str)
        
        # Test with list
        result = make_str([1, 2, 3])
        assert result == "[1, 2, 3]"
        assert isinstance(result, str)
