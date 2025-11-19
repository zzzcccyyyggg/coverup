# file: src/click/src/click/_compat.py:140-148
# asked: {"lines": [140, 141, 142, 143, 144, 145, 146, 147, 148], "branches": [[142, 143], [142, 144]]}
# gained: {"lines": [140, 141, 142, 143, 144, 145, 146, 147, 148], "branches": [[142, 143], [142, 144]]}

import pytest
import typing as t
from unittest.mock import Mock, MagicMock
import io
from click._compat import _FixupStream

class TestFixupStreamSeekable:
    """Test cases for _FixupStream.seekable() method to achieve full coverage."""
    
    def test_seekable_with_seekable_method(self):
        """Test when stream has seekable method that returns True."""
        mock_stream = Mock()
        mock_stream.seekable = Mock(return_value=True)
        fixup_stream = _FixupStream(mock_stream)
        
        result = fixup_stream.seekable()
        
        assert result is True
        mock_stream.seekable.assert_called_once()
    
    def test_seekable_with_seekable_method_false(self):
        """Test when stream has seekable method that returns False."""
        mock_stream = Mock()
        mock_stream.seekable = Mock(return_value=False)
        fixup_stream = _FixupStream(mock_stream)
        
        result = fixup_stream.seekable()
        
        assert result is False
        mock_stream.seekable.assert_called_once()
    
    def test_seekable_without_seekable_method_seek_succeeds(self):
        """Test when stream has no seekable method but seek/tell works."""
        mock_stream = Mock()
        mock_stream.seekable = None
        mock_stream.tell = Mock(return_value=0)
        mock_stream.seek = Mock()
        fixup_stream = _FixupStream(mock_stream)
        
        result = fixup_stream.seekable()
        
        assert result is True
        mock_stream.seek.assert_called_once_with(0)
        mock_stream.tell.assert_called_once()
    
    def test_seekable_without_seekable_method_seek_fails(self):
        """Test when stream has no seekable method and seek raises exception."""
        mock_stream = Mock()
        mock_stream.seekable = None
        mock_stream.tell = Mock(return_value=0)
        mock_stream.seek = Mock(side_effect=OSError("Not seekable"))
        fixup_stream = _FixupStream(mock_stream)
        
        result = fixup_stream.seekable()
        
        assert result is False
        mock_stream.seek.assert_called_once_with(0)
        mock_stream.tell.assert_called_once()
    
    def test_seekable_without_seekable_method_tell_fails(self):
        """Test when stream has no seekable method and tell raises exception."""
        mock_stream = Mock()
        mock_stream.seekable = None
        mock_stream.tell = Mock(side_effect=OSError("No position"))
        mock_stream.seek = Mock()
        fixup_stream = _FixupStream(mock_stream)
        
        result = fixup_stream.seekable()
        
        assert result is False
        mock_stream.tell.assert_called_once()
        mock_stream.seek.assert_not_called()
