# file: src/click/src/click/_compat.py:113-123
# asked: {"lines": [113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123], "branches": [[114, 115], [114, 116], [117, 118], [117, 119]]}
# gained: {"lines": [113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123], "branches": [[114, 115], [114, 116], [117, 118], [117, 119]]}

import pytest
import typing as t
from unittest.mock import Mock, patch
import io
from click._compat import _FixupStream

class TestFixupStreamReadable:
    """Test cases for _FixupStream.readable() method to achieve full coverage."""
    
    def test_readable_force_readable_true(self):
        """Test when _force_readable is True - should return True immediately."""
        # Create a mock stream
        mock_stream = Mock()
        # Create _FixupStream with force_readable=True
        fixup_stream = _FixupStream(mock_stream, force_readable=True)
        
        # Should return True without checking the stream
        assert fixup_stream.readable() is True
        
    def test_readable_with_readable_method_returns_true(self):
        """Test when stream has readable method that returns True."""
        mock_stream = Mock()
        mock_stream.readable = Mock(return_value=True)
        
        fixup_stream = _FixupStream(mock_stream, force_readable=False)
        
        assert fixup_stream.readable() is True
        mock_stream.readable.assert_called_once()
        
    def test_readable_with_readable_method_returns_false(self):
        """Test when stream has readable method that returns False."""
        mock_stream = Mock()
        mock_stream.readable = Mock(return_value=False)
        
        fixup_stream = _FixupStream(mock_stream, force_readable=False)
        
        assert fixup_stream.readable() is False
        mock_stream.readable.assert_called_once()
        
    def test_readable_no_readable_method_read_succeeds(self):
        """Test when stream has no readable method but read(0) succeeds."""
        mock_stream = Mock()
        # Remove readable attribute to simulate stream without readable method
        delattr(mock_stream, 'readable')
        mock_stream.read = Mock(return_value=b'')
        
        fixup_stream = _FixupStream(mock_stream, force_readable=False)
        
        assert fixup_stream.readable() is True
        mock_stream.read.assert_called_once_with(0)
        
    def test_readable_no_readable_method_read_raises_exception(self):
        """Test when stream has no readable method and read(0) raises exception."""
        mock_stream = Mock()
        # Remove readable attribute to simulate stream without readable method
        delattr(mock_stream, 'readable')
        mock_stream.read = Mock(side_effect=Exception("Read failed"))
        
        fixup_stream = _FixupStream(mock_stream, force_readable=False)
        
        assert fixup_stream.readable() is False
        mock_stream.read.assert_called_once_with(0)
        
    def test_readable_with_real_bytesio_stream(self):
        """Test with a real BytesIO stream (should be readable)."""
        stream = io.BytesIO(b"test data")
        fixup_stream = _FixupStream(stream, force_readable=False)
        
        assert fixup_stream.readable() is True
        
    def test_readable_with_non_readable_mock(self):
        """Test with a mock that explicitly has no readable capability."""
        mock_stream = Mock()
        # Remove readable attribute to simulate stream without readable method
        delattr(mock_stream, 'readable')
        # Simulate a stream that doesn't support reading
        mock_stream.read = Mock(side_effect=io.UnsupportedOperation("not readable"))
        
        fixup_stream = _FixupStream(mock_stream, force_readable=False)
        
        assert fixup_stream.readable() is False
        mock_stream.read.assert_called_once_with(0)
