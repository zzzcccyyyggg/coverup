# file: src/click/src/click/_compat.py:125-138
# asked: {"lines": [125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138], "branches": [[126, 127], [126, 128], [129, 130], [129, 131]]}
# gained: {"lines": [125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138], "branches": [[126, 127], [126, 128], [129, 130], [129, 131]]}

import pytest
import typing as t
from unittest.mock import Mock, patch
import io


class TestFixupStreamWritable:
    """Test cases for _FixupStream.writable() method to achieve full coverage."""
    
    def test_writable_force_writable_true(self):
        """Test when _force_writable is True - should return True immediately."""
        from click._compat import _FixupStream
        
        mock_stream = Mock()
        fixup_stream = _FixupStream(mock_stream, force_writable=True)
        
        result = fixup_stream.writable()
        
        assert result is True
        # Should not call any methods on the stream when force_writable is True
        mock_stream.writable.assert_not_called()
        mock_stream.write.assert_not_called()
    
    def test_writable_with_writable_method_returns_true(self):
        """Test when stream has writable method that returns True."""
        from click._compat import _FixupStream
        
        mock_stream = Mock()
        mock_stream.writable.return_value = True
        fixup_stream = _FixupStream(mock_stream, force_writable=False)
        
        result = fixup_stream.writable()
        
        assert result is True
        mock_stream.writable.assert_called_once()
        mock_stream.write.assert_not_called()
    
    def test_writable_with_writable_method_returns_false(self):
        """Test when stream has writable method that returns False."""
        from click._compat import _FixupStream
        
        mock_stream = Mock()
        mock_stream.writable.return_value = False
        fixup_stream = _FixupStream(mock_stream, force_writable=False)
        
        result = fixup_stream.writable()
        
        assert result is False
        mock_stream.writable.assert_called_once()
        mock_stream.write.assert_not_called()
    
    def test_writable_no_writable_method_write_succeeds(self):
        """Test when stream has no writable method but write succeeds."""
        from click._compat import _FixupStream
        
        mock_stream = Mock()
        # Remove writable attribute to simulate stream without writable method
        delattr(mock_stream, 'writable')
        mock_stream.write.return_value = None  # Write succeeds
        fixup_stream = _FixupStream(mock_stream, force_writable=False)
        
        result = fixup_stream.writable()
        
        assert result is True
        # Should call write only once when it succeeds
        assert mock_stream.write.call_count == 1
        mock_stream.write.assert_called_with(b"")
    
    def test_writable_no_writable_method_write_fails_twice(self):
        """Test when stream has no writable method and write fails twice."""
        from click._compat import _FixupStream
        
        mock_stream = Mock()
        # Remove writable attribute to simulate stream without writable method
        delattr(mock_stream, 'writable')
        mock_stream.write.side_effect = OSError("Write failed")
        fixup_stream = _FixupStream(mock_stream, force_writable=False)
        
        result = fixup_stream.writable()
        
        assert result is False
        # Should call write twice (once in try, once in except)
        assert mock_stream.write.call_count == 2
        mock_stream.write.assert_called_with(b"")
    
    def test_writable_no_writable_method_write_fails_once_then_succeeds(self):
        """Test when stream has no writable method, write fails once then succeeds."""
        from click._compat import _FixupStream
        
        mock_stream = Mock()
        # Remove writable attribute to simulate stream without writable method
        delattr(mock_stream, 'writable')
        # First call fails, second call succeeds
        mock_stream.write.side_effect = [OSError("Write failed"), None]
        fixup_stream = _FixupStream(mock_stream, force_writable=False)
        
        result = fixup_stream.writable()
        
        assert result is True
        # Should call write twice (once in try, once in except)
        assert mock_stream.write.call_count == 2
        mock_stream.write.assert_called_with(b"")
