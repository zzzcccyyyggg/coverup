# file: src/click/src/click/_termui_impl.py:844-852
# asked: {"lines": [844, 845, 846, 848, 849, 851, 852], "branches": [[848, 849], [848, 851]]}
# gained: {"lines": [844, 845, 846, 848, 849, 851, 852], "branches": [[848, 849], [848, 851]]}

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from click._termui_impl import getchar, _translate_ch_to_exc
from click._compat import WIN


class TestGetchar:
    def test_getchar_with_echo_and_tty(self, monkeypatch):
        """Test getchar when echo is True and stdout is a TTY"""
        mock_read_data = b'test_char'
        mock_encoding = 'utf-8'
        
        # Mock raw_terminal context manager
        mock_fd = 5
        mock_raw_terminal = MagicMock()
        mock_raw_terminal.__enter__ = MagicMock(return_value=mock_fd)
        mock_raw_terminal.__exit__ = MagicMock(return_value=None)
        
        # Mock os.read to return test data
        monkeypatch.setattr(os, 'read', MagicMock(return_value=mock_read_data))
        
        # Mock get_best_encoding
        monkeypatch.setattr('click._termui_impl.get_best_encoding', MagicMock(return_value=mock_encoding))
        
        # Mock isatty to return True for stdout
        monkeypatch.setattr('click._termui_impl.isatty', MagicMock(return_value=True))
        
        # Mock sys.stdout.write
        mock_stdout_write = MagicMock()
        monkeypatch.setattr(sys.stdout, 'write', mock_stdout_write)
        
        # Mock _translate_ch_to_exc to do nothing
        monkeypatch.setattr('click._termui_impl._translate_ch_to_exc', MagicMock())
        
        with patch('click._termui_impl.raw_terminal', return_value=mock_raw_terminal):
            result = getchar(echo=True)
        
        # Verify the character was written to stdout
        mock_stdout_write.assert_called_once_with('test_char')
        assert result == 'test_char'

    def test_getchar_without_echo(self, monkeypatch):
        """Test getchar when echo is False"""
        mock_read_data = b'test_char'
        mock_encoding = 'utf-8'
        
        # Mock raw_terminal context manager
        mock_fd = 5
        mock_raw_terminal = MagicMock()
        mock_raw_terminal.__enter__ = MagicMock(return_value=mock_fd)
        mock_raw_terminal.__exit__ = MagicMock(return_value=None)
        
        # Mock os.read to return test data
        monkeypatch.setattr(os, 'read', MagicMock(return_value=mock_read_data))
        
        # Mock get_best_encoding
        monkeypatch.setattr('click._termui_impl.get_best_encoding', MagicMock(return_value=mock_encoding))
        
        # Mock isatty to return True for stdout
        monkeypatch.setattr('click._termui_impl.isatty', MagicMock(return_value=True))
        
        # Mock sys.stdout.write
        mock_stdout_write = MagicMock()
        monkeypatch.setattr(sys.stdout, 'write', mock_stdout_write)
        
        # Mock _translate_ch_to_exc to do nothing
        monkeypatch.setattr('click._termui_impl._translate_ch_to_exc', MagicMock())
        
        with patch('click._termui_impl.raw_terminal', return_value=mock_raw_terminal):
            result = getchar(echo=False)
        
        # Verify nothing was written to stdout
        mock_stdout_write.assert_not_called()
        assert result == 'test_char'

    def test_getchar_echo_with_non_tty_stdout(self, monkeypatch):
        """Test getchar when echo is True but stdout is not a TTY"""
        mock_read_data = b'test_char'
        mock_encoding = 'utf-8'
        
        # Mock raw_terminal context manager
        mock_fd = 5
        mock_raw_terminal = MagicMock()
        mock_raw_terminal.__enter__ = MagicMock(return_value=mock_fd)
        mock_raw_terminal.__exit__ = MagicMock(return_value=None)
        
        # Mock os.read to return test data
        monkeypatch.setattr(os, 'read', MagicMock(return_value=mock_read_data))
        
        # Mock get_best_encoding
        monkeypatch.setattr('click._termui_impl.get_best_encoding', MagicMock(return_value=mock_encoding))
        
        # Mock isatty to return False for stdout
        monkeypatch.setattr('click._termui_impl.isatty', MagicMock(return_value=False))
        
        # Mock sys.stdout.write
        mock_stdout_write = MagicMock()
        monkeypatch.setattr(sys.stdout, 'write', mock_stdout_write)
        
        # Mock _translate_ch_to_exc to do nothing
        monkeypatch.setattr('click._termui_impl._translate_ch_to_exc', MagicMock())
        
        with patch('click._termui_impl.raw_terminal', return_value=mock_raw_terminal):
            result = getchar(echo=True)
        
        # Verify nothing was written to stdout since it's not a TTY
        mock_stdout_write.assert_not_called()
        assert result == 'test_char'

    def test_getchar_with_keyboard_interrupt_char(self, monkeypatch):
        """Test getchar when Ctrl+C character is read"""
        mock_read_data = b'\x03'  # Ctrl+C
        mock_encoding = 'utf-8'
        
        # Mock raw_terminal context manager
        mock_fd = 5
        mock_raw_terminal = MagicMock()
        mock_raw_terminal.__enter__ = MagicMock(return_value=mock_fd)
        mock_raw_terminal.__exit__ = MagicMock(return_value=None)
        
        # Mock os.read to return Ctrl+C
        monkeypatch.setattr(os, 'read', MagicMock(return_value=mock_read_data))
        
        # Mock get_best_encoding
        monkeypatch.setattr('click._termui_impl.get_best_encoding', MagicMock(return_value=mock_encoding))
        
        # Mock isatty to return False to avoid stdout write
        monkeypatch.setattr('click._termui_impl.isatty', MagicMock(return_value=False))
        
        with patch('click._termui_impl.raw_terminal', return_value=mock_raw_terminal):
            with pytest.raises(KeyboardInterrupt):
                getchar(echo=False)

    def test_getchar_with_eof_char_unix(self, monkeypatch):
        """Test getchar when EOF character is read on Unix"""
        mock_read_data = b'\x04'  # Ctrl+D
        mock_encoding = 'utf-8'
        
        # Mock raw_terminal context manager
        mock_fd = 5
        mock_raw_terminal = MagicMock()
        mock_raw_terminal.__enter__ = MagicMock(return_value=mock_fd)
        mock_raw_terminal.__exit__ = MagicMock(return_value=None)
        
        # Mock os.read to return Ctrl+D
        monkeypatch.setattr(os, 'read', MagicMock(return_value=mock_read_data))
        
        # Mock get_best_encoding
        monkeypatch.setattr('click._termui_impl.get_best_encoding', MagicMock(return_value=mock_encoding))
        
        # Mock isatty to return False to avoid stdout write
        monkeypatch.setattr('click._termui_impl.isatty', MagicMock(return_value=False))
        
        # Mock WIN to be False (Unix-like system)
        monkeypatch.setattr('click._termui_impl.WIN', False)
        
        with patch('click._termui_impl.raw_terminal', return_value=mock_raw_terminal):
            with pytest.raises(EOFError):
                getchar(echo=False)

    def test_getchar_with_eof_char_windows(self, monkeypatch):
        """Test getchar when EOF character is read on Windows"""
        mock_read_data = b'\x1a'  # Ctrl+Z
        mock_encoding = 'utf-8'
        
        # Mock raw_terminal context manager
        mock_fd = 5
        mock_raw_terminal = MagicMock()
        mock_raw_terminal.__enter__ = MagicMock(return_value=mock_fd)
        mock_raw_terminal.__exit__ = MagicMock(return_value=None)
        
        # Mock os.read to return Ctrl+Z
        monkeypatch.setattr(os, 'read', MagicMock(return_value=mock_read_data))
        
        # Mock get_best_encoding
        monkeypatch.setattr('click._termui_impl.get_best_encoding', MagicMock(return_value=mock_encoding))
        
        # Mock isatty to return False to avoid stdout write
        monkeypatch.setattr('click._termui_impl.isatty', MagicMock(return_value=False))
        
        # Mock WIN to be True (Windows system)
        monkeypatch.setattr('click._termui_impl.WIN', True)
        
        with patch('click._termui_impl.raw_terminal', return_value=mock_raw_terminal):
            with pytest.raises(EOFError):
                getchar(echo=False)
