# file: src/click/src/click/_compat.py:572-576
# asked: {"lines": [572, 573, 574, 575, 576], "branches": []}
# gained: {"lines": [572, 573, 574, 575, 576], "branches": []}

import pytest
import io
from unittest.mock import Mock, patch
import click._compat


class TestIsatty:
    def test_isatty_returns_true_when_stream_is_tty(self):
        """Test that isatty returns True when stream.isatty() returns True."""
        mock_stream = Mock()
        mock_stream.isatty.return_value = True
        
        result = click._compat.isatty(mock_stream)
        
        assert result is True
        mock_stream.isatty.assert_called_once()

    def test_isatty_returns_false_when_stream_isatty_raises_exception(self):
        """Test that isatty returns False when stream.isatty() raises an exception."""
        mock_stream = Mock()
        mock_stream.isatty.side_effect = Exception("Stream error")
        
        result = click._compat.isatty(mock_stream)
        
        assert result is False
        mock_stream.isatty.assert_called_once()

    def test_isatty_with_real_stream_that_is_tty(self):
        """Test isatty with a real stream that is a TTY (using mock)."""
        with patch('sys.stdout') as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = click._compat.isatty(mock_stdout)
            assert result is True

    def test_isatty_with_real_stream_that_is_not_tty(self):
        """Test isatty with a real stream that is not a TTY (using mock)."""
        with patch('sys.stdout') as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = click._compat.isatty(mock_stdout)
            assert result is False

    def test_isatty_with_bytes_io_stream(self):
        """Test isatty with a BytesIO stream which should return False."""
        stream = io.BytesIO()
        result = click._compat.isatty(stream)
        assert result is False

    def test_isatty_with_string_io_stream(self):
        """Test isatty with a StringIO stream which should return False."""
        stream = io.StringIO()
        result = click._compat.isatty(stream)
        assert result is False
