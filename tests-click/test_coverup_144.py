# file: src/click/src/click/_termui_impl.py:554-561
# asked: {"lines": [554, 558, 559, 560, 561], "branches": [[558, 0], [558, 559], [559, 560], [559, 561]]}
# gained: {"lines": [554, 558, 559, 560, 561], "branches": [[558, 0], [558, 559], [559, 560], [559, 561]]}

import pytest
from click._termui_impl import _nullpager
from click._compat import strip_ansi
from io import StringIO


def test_nullpager_with_color_false():
    """Test _nullpager when color is False - should strip ANSI codes."""
    stream = StringIO()
    generator = ["\x1b[31mred text\x1b[0m", "normal text"]
    _nullpager(stream, generator, color=False)
    result = stream.getvalue()
    assert "red text" in result
    assert "\x1b[31m" not in result
    assert "normal text" in result


def test_nullpager_with_color_none():
    """Test _nullpager when color is None - should strip ANSI codes (None is falsy)."""
    stream = StringIO()
    generator = ["\x1b[31mred text\x1b[0m", "normal text"]
    _nullpager(stream, generator, color=None)
    result = stream.getvalue()
    assert "red text" in result
    assert "\x1b[31m" not in result
    assert "normal text" in result


def test_nullpager_with_color_true():
    """Test _nullpager when color is True - should not strip ANSI codes."""
    stream = StringIO()
    generator = ["\x1b[31mred text\x1b[0m", "normal text"]
    _nullpager(stream, generator, color=True)
    result = stream.getvalue()
    assert "\x1b[31mred text\x1b[0m" in result
    assert "normal text" in result


def test_nullpager_empty_generator():
    """Test _nullpager with empty generator."""
    stream = StringIO()
    generator = []
    _nullpager(stream, generator, color=False)
    result = stream.getvalue()
    assert result == ""
