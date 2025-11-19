# file: src/click/src/click/_compat.py:160-170
# asked: {"lines": [160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170], "branches": []}
# gained: {"lines": [160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170], "branches": []}

import pytest
import typing as t
from unittest.mock import Mock
from click._compat import _is_binary_writer


class TestIsBinaryWriter:
    """Test cases for _is_binary_writer function to achieve full coverage."""
    
    def test_binary_writer_success(self):
        """Test when stream successfully writes binary data."""
        mock_stream = Mock()
        mock_stream.write = Mock(return_value=None)
        
        result = _is_binary_writer(mock_stream)
        
        assert result is True
        mock_stream.write.assert_called_once_with(b'')
    
    def test_binary_writer_fails_but_text_succeeds(self):
        """Test when binary write fails but text write succeeds."""
        mock_stream = Mock()
        mock_stream.write = Mock(side_effect=[
            Exception("Binary write failed"),  # First call fails
            None  # Second call succeeds
        ])
        
        result = _is_binary_writer(mock_stream)
        
        assert result is False
        assert mock_stream.write.call_count == 2
        mock_stream.write.assert_any_call(b'')
        mock_stream.write.assert_any_call('')
    
    def test_both_writes_fail_with_default_false(self):
        """Test when both binary and text writes fail with default=False."""
        mock_stream = Mock()
        mock_stream.write = Mock(side_effect=Exception("Write failed"))
        
        result = _is_binary_writer(mock_stream, default=False)
        
        assert result is False
        assert mock_stream.write.call_count == 2
        mock_stream.write.assert_any_call(b'')
        mock_stream.write.assert_any_call('')
    
    def test_both_writes_fail_with_default_true(self):
        """Test when both binary and text writes fail with default=True."""
        mock_stream = Mock()
        mock_stream.write = Mock(side_effect=Exception("Write failed"))
        
        result = _is_binary_writer(mock_stream, default=True)
        
        assert result is True
        assert mock_stream.write.call_count == 2
        mock_stream.write.assert_any_call(b'')
        mock_stream.write.assert_any_call('')
