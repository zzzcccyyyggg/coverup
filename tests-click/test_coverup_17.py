# file: src/click/src/click/_compat.py:238-281
# asked: {"lines": [238, 244, 245, 247, 248, 250, 253, 254, 256, 259, 263, 264, 266, 270, 271, 275, 276, 277, 278, 279, 280], "branches": [[247, 248], [247, 250], [253, 256], [253, 259], [263, 264], [263, 266], [270, 271], [270, 275]]}
# gained: {"lines": [238, 244, 245, 247, 248, 250, 253, 254, 256, 259, 263, 264, 266, 270, 271, 275, 276, 277, 278, 279, 280], "branches": [[247, 248], [247, 250], [253, 256], [253, 259], [263, 264], [263, 266], [270, 271], [270, 275]]}

import pytest
import typing as t
from unittest.mock import Mock, MagicMock
import io

# Import the function under test
from click._compat import _force_correct_text_stream


class TestForceCorrectTextStream:
    """Test cases for _force_correct_text_stream function to achieve full coverage."""
    
    def test_binary_stream_with_errors_none(self, monkeypatch):
        """Test when input is binary stream and errors is None - should use 'replace'."""
        # Create a mock binary stream
        mock_binary_stream = Mock()
        mock_binary_stream.readable.return_value = True
        mock_binary_stream.writable.return_value = True
        
        # Mock the helper functions
        def mock_is_binary(stream, default):
            return True
            
        def mock_find_binary(stream):
            return stream
            
        # Mock _make_text_stream to capture parameters
        mock_text_stream = Mock()
        def mock_make_text_stream(binary_reader, encoding, errors, force_readable, force_writable):
            # Verify errors was set to 'replace'
            assert errors == 'replace'
            return mock_text_stream
            
        monkeypatch.setattr('click._compat._make_text_stream', mock_make_text_stream)
        
        # Call the function with errors=None
        result = _force_correct_text_stream(
            text_stream=mock_binary_stream,
            encoding='utf-8',
            errors=None,
            is_binary=mock_is_binary,
            find_binary=mock_find_binary
        )
        
        assert result is mock_text_stream
    
    def test_text_stream_incompatible_with_misconfigured_encoding(self, monkeypatch):
        """Test when text stream is incompatible and has misconfigured ASCII encoding."""
        # Create a mock text stream with ASCII encoding
        mock_text_stream = Mock()
        mock_text_stream.encoding = 'ascii'
        mock_text_stream.errors = 'strict'
        
        # Mock the helper functions
        def mock_is_binary(stream, default):
            return False
            
        def mock_find_binary(stream):
            return Mock()
            
        # Mock the compatibility check functions
        def mock_is_compatible_text_stream(stream, encoding, errors):
            return False
            
        def mock_stream_is_misconfigured(stream):
            return True
            
        monkeypatch.setattr('click._compat._is_compatible_text_stream', mock_is_compatible_text_stream)
        monkeypatch.setattr('click._compat._stream_is_misconfigured', mock_stream_is_misconfigured)
        
        # Mock _make_text_stream
        mock_result_stream = Mock()
        monkeypatch.setattr('click._compat._make_text_stream', lambda *args, **kwargs: mock_result_stream)
        
        # Call with encoding=None to trigger misconfigured check
        result = _force_correct_text_stream(
            text_stream=mock_text_stream,
            encoding=None,
            errors='strict',
            is_binary=mock_is_binary,
            find_binary=mock_find_binary
        )
        
        # Should return the wrapped stream, not the original
        assert result is mock_result_stream
    
    def test_text_stream_find_binary_returns_none(self, monkeypatch):
        """Test when text stream is incompatible but find_binary returns None."""
        # Create a mock text stream
        mock_text_stream = Mock()
        mock_text_stream.encoding = 'utf-8'
        mock_text_stream.errors = 'strict'
        
        # Mock the helper functions
        def mock_is_binary(stream, default):
            return False
            
        def mock_find_binary(stream):
            return None
            
        # Mock the compatibility check functions
        def mock_is_compatible_text_stream(stream, encoding, errors):
            return False
            
        def mock_stream_is_misconfigured(stream):
            return False
            
        monkeypatch.setattr('click._compat._is_compatible_text_stream', mock_is_compatible_text_stream)
        monkeypatch.setattr('click._compat._stream_is_misconfigured', mock_stream_is_misconfigured)
        
        # Call the function
        result = _force_correct_text_stream(
            text_stream=mock_text_stream,
            encoding='utf-8',
            errors='strict',
            is_binary=mock_is_binary,
            find_binary=mock_find_binary
        )
        
        # Should return original stream when find_binary returns None
        assert result is mock_text_stream
    
    def test_text_stream_compatible_and_not_misconfigured(self, monkeypatch):
        """Test when text stream is compatible and not misconfigured - should return as-is."""
        # Create a mock text stream
        mock_text_stream = Mock()
        mock_text_stream.encoding = 'utf-8'
        mock_text_stream.errors = 'strict'
        
        # Mock the helper functions
        def mock_is_binary(stream, default):
            return False
            
        def mock_find_binary(stream):
            return Mock()  # This shouldn't be called
        
        # Mock the compatibility check functions
        def mock_is_compatible_text_stream(stream, encoding, errors):
            return True
            
        def mock_stream_is_misconfigured(stream):
            return False
            
        monkeypatch.setattr('click._compat._is_compatible_text_stream', mock_is_compatible_text_stream)
        monkeypatch.setattr('click._compat._stream_is_misconfigured', mock_stream_is_misconfigured)
        
        # Call the function
        result = _force_correct_text_stream(
            text_stream=mock_text_stream,
            encoding='utf-8',
            errors='strict',
            is_binary=mock_is_binary,
            find_binary=mock_find_binary
        )
        
        # Should return original stream when compatible
        assert result is mock_text_stream
    
    def test_force_readable_and_writable_flags(self, monkeypatch):
        """Test that force_readable and force_writable flags are passed through."""
        # Create a mock binary stream
        mock_binary_stream = Mock()
        
        # Mock the helper functions
        def mock_is_binary(stream, default):
            return True
            
        def mock_find_binary(stream):
            return stream
            
        # Track calls to _make_text_stream
        call_args = []
        def mock_make_text_stream(binary_reader, encoding, errors, force_readable, force_writable):
            call_args.append({
                'force_readable': force_readable,
                'force_writable': force_writable
            })
            return Mock()
            
        monkeypatch.setattr('click._compat._make_text_stream', mock_make_text_stream)
        
        # Call with force flags
        _force_correct_text_stream(
            text_stream=mock_binary_stream,
            encoding='utf-8',
            errors='replace',
            is_binary=mock_is_binary,
            find_binary=mock_find_binary,
            force_readable=True,
            force_writable=True
        )
        
        # Verify flags were passed through
        assert call_args[0]['force_readable'] is True
        assert call_args[0]['force_writable'] is True
