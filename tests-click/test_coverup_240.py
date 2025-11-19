# file: src/click/src/click/_compat.py:151-155
# asked: {"lines": [151, 152, 153, 154, 155], "branches": []}
# gained: {"lines": [151, 152, 153, 154, 155], "branches": []}

import pytest
import io
import typing as t
from unittest.mock import Mock, patch


class TestIsBinaryReader:
    """Test cases for _is_binary_reader function."""
    
    def test_binary_reader_returns_true(self):
        """Test that binary stream returns True."""
        # Create a binary stream
        binary_stream = io.BytesIO(b"test data")
        from click._compat import _is_binary_reader
        
        result = _is_binary_reader(binary_stream)
        assert result is True
    
    def test_text_reader_returns_false(self):
        """Test that text stream returns False."""
        # Create a text stream
        text_stream = io.StringIO("test data")
        from click._compat import _is_binary_reader
        
        result = _is_binary_reader(text_stream)
        assert result is False
    
    def test_exception_returns_default_false(self):
        """Test that exception during read returns default False."""
        # Create a mock stream that raises an exception
        mock_stream = Mock()
        mock_stream.read.side_effect = IOError("Read failed")
        from click._compat import _is_binary_reader
        
        result = _is_binary_reader(mock_stream, default=False)
        assert result is False
    
    def test_exception_returns_default_true(self):
        """Test that exception during read returns default True."""
        # Create a mock stream that raises an exception
        mock_stream = Mock()
        mock_stream.read.side_effect = ValueError("Read failed")
        from click._compat import _is_binary_reader
        
        result = _is_binary_reader(mock_stream, default=True)
        assert result is True
    
    def test_specific_exception_types(self):
        """Test with various exception types to ensure all are caught."""
        from click._compat import _is_binary_reader
        
        # Test with different exception types
        exceptions_to_test = [
            IOError("I/O error"),
            OSError("OS error"),
            RuntimeError("Runtime error"),
            AttributeError("Attribute error"),
            TypeError("Type error")
        ]
        
        for exc in exceptions_to_test:
            mock_stream = Mock()
            mock_stream.read.side_effect = exc
            result = _is_binary_reader(mock_stream, default=False)
            assert result is False
