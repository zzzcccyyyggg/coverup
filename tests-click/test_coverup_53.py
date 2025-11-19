# file: src/click/src/click/_compat.py:19-37
# asked: {"lines": [19, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], "branches": [[26, 27], [26, 28], [28, 29], [28, 30]]}
# gained: {"lines": [19, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], "branches": [[26, 27], [26, 28], [28, 29], [28, 30]]}

import io
import pytest
import typing as t
from unittest.mock import Mock, patch


def test_make_text_stream_with_none_encoding_and_errors():
    """Test _make_text_stream when both encoding and errors are None."""
    mock_stream = Mock(spec=io.BytesIO)
    mock_stream.encoding = None
    
    with patch('click._compat.get_best_encoding', return_value='utf-8'):
        from click._compat import _make_text_stream
        
        result = _make_text_stream(
            stream=mock_stream,
            encoding=None,
            errors=None,
            force_readable=False,
            force_writable=False
        )
        
        assert isinstance(result, io.TextIOWrapper)
        assert result.encoding == 'utf-8'
        assert result.errors == 'replace'


def test_make_text_stream_with_none_encoding_only():
    """Test _make_text_stream when only encoding is None."""
    mock_stream = Mock(spec=io.BytesIO)
    mock_stream.encoding = None
    
    with patch('click._compat.get_best_encoding', return_value='latin-1'):
        from click._compat import _make_text_stream
        
        result = _make_text_stream(
            stream=mock_stream,
            encoding=None,
            errors='strict',
            force_readable=True,
            force_writable=False
        )
        
        assert isinstance(result, io.TextIOWrapper)
        assert result.encoding == 'latin-1'
        assert result.errors == 'strict'


def test_make_text_stream_with_none_errors_only():
    """Test _make_text_stream when only errors is None."""
    mock_stream = Mock(spec=io.BytesIO)
    
    from click._compat import _make_text_stream
    
    result = _make_text_stream(
        stream=mock_stream,
        encoding='utf-8',
        errors=None,
        force_readable=False,
        force_writable=True
    )
    
    assert isinstance(result, io.TextIOWrapper)
    assert result.encoding == 'utf-8'
    assert result.errors == 'replace'


def test_make_text_stream_with_force_readable_and_writable():
    """Test _make_text_stream with both force_readable and force_writable set to True."""
    mock_stream = Mock(spec=io.BytesIO)
    
    from click._compat import _make_text_stream
    
    result = _make_text_stream(
        stream=mock_stream,
        encoding='ascii',
        errors='ignore',
        force_readable=True,
        force_writable=True
    )
    
    assert isinstance(result, io.TextIOWrapper)
    assert result.encoding == 'ascii'
    assert result.errors == 'ignore'
