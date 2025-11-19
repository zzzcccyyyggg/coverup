# file: src/click/src/click/_compat.py:227-235
# asked: {"lines": [227, 233, 234, 235], "branches": []}
# gained: {"lines": [227, 233, 234, 235], "branches": []}

import pytest
import typing as t
from io import StringIO
from unittest.mock import Mock


class TestIsCompatibleTextStream:
    """Test cases for _is_compatible_text_stream function."""
    
    def test_compatible_encoding_and_errors(self):
        """Test when both encoding and errors are compatible."""
        # Create a mock stream with the desired attributes
        stream = Mock()
        stream.encoding = "utf-8"
        stream.errors = "strict"
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, "utf-8", "strict")
        assert result is True
    
    def test_compatible_with_none_values(self):
        """Test when desired encoding and errors are None."""
        # Create a mock stream with the desired attributes
        stream = Mock()
        stream.encoding = "utf-8"
        stream.errors = "strict"
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, None, None)
        assert result is True
    
    def test_incompatible_encoding(self):
        """Test when encoding is incompatible."""
        # Create a mock stream with the desired attributes
        stream = Mock()
        stream.encoding = "utf-8"
        stream.errors = "strict"
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, "ascii", "strict")
        assert result is False
    
    def test_incompatible_errors(self):
        """Test when errors are incompatible."""
        # Create a mock stream with the desired attributes
        stream = Mock()
        stream.encoding = "utf-8"
        stream.errors = "strict"
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, "utf-8", "ignore")
        assert result is False
    
    def test_incompatible_both(self):
        """Test when both encoding and errors are incompatible."""
        # Create a mock stream with the desired attributes
        stream = Mock()
        stream.encoding = "utf-8"
        stream.errors = "strict"
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, "ascii", "ignore")
        assert result is False
    
    def test_stream_without_encoding_attribute(self):
        """Test with stream that doesn't have encoding attribute."""
        stream = Mock()
        stream.encoding = None
        stream.errors = "strict"
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, "utf-8", "strict")
        assert result is False
    
    def test_stream_without_errors_attribute(self):
        """Test with stream that doesn't have errors attribute."""
        stream = Mock()
        stream.encoding = "utf-8"
        stream.errors = None
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, "utf-8", "strict")
        assert result is False
    
    def test_stream_without_both_attributes(self):
        """Test with stream that has neither encoding nor errors attributes."""
        stream = Mock(spec=[])
        
        from click._compat import _is_compatible_text_stream
        result = _is_compatible_text_stream(stream, "utf-8", "strict")
        assert result is False
