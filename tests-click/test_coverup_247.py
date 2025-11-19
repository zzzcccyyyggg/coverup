# file: src/click/src/click/_compat.py:105-111
# asked: {"lines": [105, 106, 108, 109, 111], "branches": [[108, 109], [108, 111]]}
# gained: {"lines": [105, 106, 108, 109, 111], "branches": [[108, 109], [108, 111]]}

import pytest
import typing as t
from unittest.mock import Mock, MagicMock
import io


class TestFixupStreamRead1:
    """Test cases for _FixupStream.read1 method to achieve full coverage."""
    
    def test_read1_with_read1_method(self):
        """Test read1 when underlying stream has read1 method."""
        # Create a mock stream with read1 method
        mock_stream = Mock()
        mock_stream.read1 = Mock(return_value=b"test data")
        
        # Create _FixupStream instance
        from click._compat import _FixupStream
        fixup_stream = _FixupStream(mock_stream)
        
        # Call read1 method
        result = fixup_stream.read1(10)
        
        # Verify read1 was called on underlying stream
        mock_stream.read1.assert_called_once_with(10)
        assert result == b"test data"
    
    def test_read1_without_read1_method(self):
        """Test read1 when underlying stream does not have read1 method."""
        # Create a mock stream without read1 method
        mock_stream = Mock(spec=['read'])
        mock_stream.read = Mock(return_value=b"fallback data")
        
        # Create _FixupStream instance
        from click._compat import _FixupStream
        fixup_stream = _FixupStream(mock_stream)
        
        # Call read1 method
        result = fixup_stream.read1(10)
        
        # Verify read was called on underlying stream (fallback)
        mock_stream.read.assert_called_once_with(10)
        assert result == b"fallback data"
    
    def test_read1_with_read1_as_none(self):
        """Test read1 when getattr returns None for read1 attribute."""
        # Create a mock stream where read1 attribute exists but is None
        mock_stream = Mock()
        mock_stream.read1 = None  # Explicitly set read1 to None
        mock_stream.read = Mock(return_value=b"no read1 data")
        
        # Create _FixupStream instance
        from click._compat import _FixupStream
        fixup_stream = _FixupStream(mock_stream)
        
        # Call read1 method
        result = fixup_stream.read1(5)
        
        # Verify read was called as fallback
        mock_stream.read.assert_called_once_with(5)
        assert result == b"no read1 data"
