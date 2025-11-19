# file: src/click/src/click/exceptions.py:26-53
# asked: {"lines": [26, 27, 30, 32, 33, 36, 37, 39, 40, 42, 43, 45, 46, 47, 49, 50, 51, 52], "branches": [[46, 47], [46, 49]]}
# gained: {"lines": [26, 27, 30, 32, 33, 36, 37, 39, 40, 42, 43, 45, 46, 47, 49, 50, 51, 52], "branches": [[46, 47], [46, 49]]}

import pytest
import io
from unittest.mock import patch, MagicMock
from click.exceptions import ClickException
from click._compat import get_text_stderr
from click.utils import echo


class TestClickException:
    def test_click_exception_init(self):
        """Test ClickException initialization with message."""
        message = "Test error message"
        exc = ClickException(message)
        assert exc.message == message
        assert str(exc) == message
        assert exc.exit_code == 1

    def test_click_exception_format_message(self):
        """Test ClickException format_message method."""
        message = "Test error message"
        exc = ClickException(message)
        assert exc.format_message() == message

    def test_click_exception_show_with_none_file(self):
        """Test ClickException show method when file is None."""
        message = "Test error message"
        exc = ClickException(message)
        
        with patch('click.exceptions.get_text_stderr') as mock_get_stderr, \
             patch('click.exceptions.echo') as mock_echo:
            mock_stderr = io.StringIO()
            mock_get_stderr.return_value = mock_stderr
            
            exc.show()
            
            mock_get_stderr.assert_called_once()
            mock_echo.assert_called_once_with(
                "Error: Test error message",
                file=mock_stderr,
                color=exc.show_color
            )

    def test_click_exception_show_with_custom_file(self):
        """Test ClickException show method with custom file."""
        message = "Test error message"
        exc = ClickException(message)
        custom_file = io.StringIO()
        
        with patch('click.exceptions.echo') as mock_echo:
            exc.show(file=custom_file)
            
            mock_echo.assert_called_once_with(
                "Error: Test error message",
                file=custom_file,
                color=exc.show_color
            )

    def test_click_exception_show_color_resolution(self):
        """Test ClickException show method with different color settings."""
        message = "Test error message"
        
        # Test with different color values by patching resolve_color_default
        test_cases = [
            (True, True),
            (False, False),
            (None, None)
        ]
        
        for expected_color, mock_return in test_cases:
            with patch('click.exceptions.resolve_color_default', return_value=mock_return):
                exc = ClickException(message)
                assert exc.show_color == expected_color

    def test_click_exception_inheritance(self):
        """Test that ClickException properly inherits from Exception."""
        message = "Test error message"
        exc = ClickException(message)
        
        assert isinstance(exc, Exception)
        assert isinstance(exc, ClickException)
        assert exc.args == (message,)
