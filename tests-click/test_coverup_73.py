# file: src/click/src/click/_termui_impl.py:747-757
# asked: {"lines": [747, 748, 749, 751, 752, 754, 755, 757], "branches": [[748, 749], [748, 751], [751, 752], [751, 754], [754, 755], [754, 757]]}
# gained: {"lines": [747, 748, 749, 751, 752, 754, 757], "branches": [[748, 749], [748, 751], [751, 752], [751, 754], [754, 757]]}

import pytest
from click._termui_impl import _translate_ch_to_exc
from click._compat import WIN


def test_translate_ch_to_exc_keyboard_interrupt():
    """Test that Ctrl+C (\\x03) raises KeyboardInterrupt."""
    with pytest.raises(KeyboardInterrupt):
        _translate_ch_to_exc("\x03")


def test_translate_ch_to_exc_eof_unix():
    """Test that Ctrl+D (\\x04) raises EOFError on Unix-like systems."""
    if not WIN:
        with pytest.raises(EOFError):
            _translate_ch_to_exc("\x04")
    else:
        # On Windows, Ctrl+D should not raise EOFError
        assert _translate_ch_to_exc("\x04") is None


def test_translate_ch_to_exc_eof_windows():
    """Test that Ctrl+Z (\\x1a) raises EOFError on Windows."""
    if WIN:
        with pytest.raises(EOFError):
            _translate_ch_to_exc("\x1a")
    else:
        # On Unix-like systems, Ctrl+Z should not raise EOFError
        assert _translate_ch_to_exc("\x1a") is None


def test_translate_ch_to_exc_no_exception():
    """Test that other characters return None without raising exceptions."""
    assert _translate_ch_to_exc("a") is None
    assert _translate_ch_to_exc("\x00") is None
    assert _translate_ch_to_exc("\n") is None
