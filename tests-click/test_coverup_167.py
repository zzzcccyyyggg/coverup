# file: src/click/src/click/utils.py:337-355
# asked: {"lines": [337, 339, 340, 352, 353, 354, 355], "branches": [[353, 354], [353, 355]]}
# gained: {"lines": [337, 339, 340, 352, 353, 354, 355], "branches": [[353, 354], [353, 355]]}

import pytest
import typing as t
from click.utils import get_text_stream
from click._compat import text_streams


class TestGetTextStream:
    """Test cases for get_text_stream function to achieve full coverage."""
    
    def test_get_text_stream_stdin(self):
        """Test get_text_stream with 'stdin'."""
        stream = get_text_stream('stdin')
        assert stream is not None
        assert hasattr(stream, 'read')
    
    def test_get_text_stream_stdout(self):
        """Test get_text_stream with 'stdout'."""
        stream = get_text_stream('stdout')
        assert stream is not None
        assert hasattr(stream, 'write')
    
    def test_get_text_stream_stderr(self):
        """Test get_text_stream with 'stderr'."""
        stream = get_text_stream('stderr')
        assert stream is not None
        assert hasattr(stream, 'write')
    
    def test_get_text_stream_with_encoding(self):
        """Test get_text_stream with custom encoding."""
        stream = get_text_stream('stdout', encoding='utf-8')
        assert stream is not None
        assert hasattr(stream, 'write')
    
    def test_get_text_stream_with_errors(self):
        """Test get_text_stream with custom error handling."""
        stream = get_text_stream('stdout', errors='replace')
        assert stream is not None
        assert hasattr(stream, 'write')
    
    def test_get_text_stream_with_encoding_and_errors(self):
        """Test get_text_stream with both encoding and errors."""
        stream = get_text_stream('stdout', encoding='utf-8', errors='ignore')
        assert stream is not None
        assert hasattr(stream, 'write')
    
    def test_get_text_stream_unknown_stream(self, monkeypatch):
        """Test get_text_stream with unknown stream name raises TypeError."""
        # Create a mock text_streams dict that doesn't have the unknown stream
        mock_text_streams = {
            'stdin': text_streams['stdin'],
            'stdout': text_streams['stdout'], 
            'stderr': text_streams['stderr']
        }
        
        # Patch the text_streams import in the click.utils module
        monkeypatch.setattr('click.utils.text_streams', mock_text_streams)
        
        with pytest.raises(TypeError) as exc_info:
            get_text_stream('unknown')
        
        assert "Unknown standard stream 'unknown'" in str(exc_info.value)
