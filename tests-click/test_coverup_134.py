# file: src/click/src/click/termui.py:659-690
# asked: {"lines": [659, 660, 661, 662, 663, 664, 687, 688, 690], "branches": [[687, 688], [687, 690]]}
# gained: {"lines": [659, 660, 661, 662, 663, 664, 687, 688, 690], "branches": [[687, 688], [687, 690]]}

import pytest
import io
from unittest.mock import patch, MagicMock
import click


def test_secho_with_string_message_and_styles():
    """Test secho with string message and styles applied."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        mock_style.return_value = "styled_message"
        
        click.secho("test message", fg="red", bold=True)
        
        mock_style.assert_called_once_with("test message", fg="red", bold=True)
        mock_echo.assert_called_once_with("styled_message", file=None, nl=True, err=False, color=None)


def test_secho_with_non_string_message():
    """Test secho with non-string message that gets converted and styled."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        mock_style.return_value = "styled_123"
        
        click.secho(123, fg="blue")
        
        mock_style.assert_called_once_with(123, fg="blue")
        mock_echo.assert_called_once_with("styled_123", file=None, nl=True, err=False, color=None)


def test_secho_with_bytes_message():
    """Test secho with bytes message - should not apply styles."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        
        click.secho(b"bytes message", fg="green")
        
        mock_style.assert_not_called()
        mock_echo.assert_called_once_with(b"bytes message", file=None, nl=True, err=False, color=None)


def test_secho_with_bytearray_message():
    """Test secho with bytearray message - should not apply styles."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        
        click.secho(bytearray(b"bytearray message"), fg="yellow")
        
        mock_style.assert_not_called()
        mock_echo.assert_called_once_with(bytearray(b"bytearray message"), file=None, nl=True, err=False, color=None)


def test_secho_with_none_message():
    """Test secho with None message - should not apply styles."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        
        click.secho(None, fg="red")
        
        mock_style.assert_not_called()
        mock_echo.assert_called_once_with(None, file=None, nl=True, err=False, color=None)


def test_secho_with_custom_file():
    """Test secho with custom file parameter."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        mock_style.return_value = "styled_message"
        custom_file = io.StringIO()
        
        click.secho("test", file=custom_file, fg="red")
        
        mock_style.assert_called_once_with("test", fg="red")
        mock_echo.assert_called_once_with("styled_message", file=custom_file, nl=True, err=False, color=None)


def test_secho_with_err_true():
    """Test secho with err=True."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        mock_style.return_value = "styled_message"
        
        click.secho("test", err=True, fg="red")
        
        mock_style.assert_called_once_with("test", fg="red")
        mock_echo.assert_called_once_with("styled_message", file=None, nl=True, err=True, color=None)


def test_secho_with_nl_false():
    """Test secho with nl=False."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        mock_style.return_value = "styled_message"
        
        click.secho("test", nl=False, fg="red")
        
        mock_style.assert_called_once_with("test", fg="red")
        mock_echo.assert_called_once_with("styled_message", file=None, nl=False, err=False, color=None)


def test_secho_with_color_parameter():
    """Test secho with explicit color parameter."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        mock_style.return_value = "styled_message"
        
        click.secho("test", color=True, fg="red")
        
        mock_style.assert_called_once_with("test", fg="red")
        mock_echo.assert_called_once_with("styled_message", file=None, nl=True, err=False, color=True)


def test_secho_with_multiple_styles():
    """Test secho with multiple style parameters."""
    with patch('click.termui.style') as mock_style, \
         patch('click.termui.echo') as mock_echo:
        mock_style.return_value = "styled_message"
        
        click.secho("test", fg="red", bg="blue", bold=True, underline=True)
        
        mock_style.assert_called_once_with("test", fg="red", bg="blue", bold=True, underline=True)
        mock_echo.assert_called_once_with("styled_message", file=None, nl=True, err=False, color=None)
