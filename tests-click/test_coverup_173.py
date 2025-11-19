# file: src/click/src/click/_compat.py:499-506
# asked: {"lines": [499, 500, 502, 503, 504, 505, 506], "branches": [[502, 503], [502, 506], [503, 504], [503, 505]]}
# gained: {"lines": [499, 500, 502, 503, 504, 505, 506], "branches": [[502, 503], [502, 506], [503, 504], [503, 505]]}

import pytest
import sys
import typing as t
from unittest.mock import Mock, patch
from io import StringIO

class _FixupStream:
    def __init__(self, stream):
        self._stream = stream

class _NonClosingTextIOWrapper:
    def __init__(self, stream):
        self._stream = stream

def test_should_strip_ansi_color_none_stream_none():
    """Test when color is None and stream is None - should use sys.stdin"""
    with patch('click._compat.isatty') as mock_isatty, \
         patch('click._compat._is_jupyter_kernel_output') as mock_jupyter:
        mock_isatty.return_value = False
        mock_jupyter.return_value = False
        
        from click._compat import should_strip_ansi
        result = should_strip_ansi(color=None, stream=None)
        
        assert result is True
        mock_isatty.assert_called_once_with(sys.stdin)
        mock_jupyter.assert_called_once_with(sys.stdin)

def test_should_strip_ansi_color_none_stream_not_tty_not_jupyter():
    """Test when color is None, stream provided, not tty, not jupyter"""
    stream = StringIO()
    
    with patch('click._compat.isatty') as mock_isatty, \
         patch('click._compat._is_jupyter_kernel_output') as mock_jupyter:
        mock_isatty.return_value = False
        mock_jupyter.return_value = False
        
        from click._compat import should_strip_ansi
        result = should_strip_ansi(color=None, stream=stream)
        
        assert result is True
        mock_isatty.assert_called_once_with(stream)
        mock_jupyter.assert_called_once_with(stream)

def test_should_strip_ansi_color_none_stream_is_tty():
    """Test when color is None, stream is tty - short-circuit evaluation"""
    stream = StringIO()
    
    with patch('click._compat.isatty') as mock_isatty, \
         patch('click._compat._is_jupyter_kernel_output') as mock_jupyter:
        mock_isatty.return_value = True
        mock_jupyter.return_value = False
        
        from click._compat import should_strip_ansi
        result = should_strip_ansi(color=None, stream=stream)
        
        assert result is False
        mock_isatty.assert_called_once_with(stream)
        # _is_jupyter_kernel_output should NOT be called due to short-circuit evaluation
        mock_jupyter.assert_not_called()

def test_should_strip_ansi_color_none_stream_is_jupyter():
    """Test when color is None, stream is jupyter kernel output"""
    stream = StringIO()
    
    with patch('click._compat.isatty') as mock_isatty, \
         patch('click._compat._is_jupyter_kernel_output') as mock_jupyter:
        mock_isatty.return_value = False
        mock_jupyter.return_value = True
        
        from click._compat import should_strip_ansi
        result = should_strip_ansi(color=None, stream=stream)
        
        assert result is False
        mock_isatty.assert_called_once_with(stream)
        mock_jupyter.assert_called_once_with(stream)

def test_should_strip_ansi_color_false():
    """Test when color is False"""
    from click._compat import should_strip_ansi
    result = should_strip_ansi(color=False)
    assert result is True

def test_should_strip_ansi_color_true():
    """Test when color is True"""
    from click._compat import should_strip_ansi
    result = should_strip_ansi(color=True)
    assert result is False
