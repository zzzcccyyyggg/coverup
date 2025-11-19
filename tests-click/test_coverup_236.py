# file: src/click/src/click/_compat.py:40-45
# asked: {"lines": [40, 42, 43, 44, 45], "branches": []}
# gained: {"lines": [40, 42, 43, 44, 45], "branches": []}

import pytest
import codecs
from click._compat import is_ascii_encoding


def test_is_ascii_encoding_ascii():
    """Test that ascii encoding returns True."""
    result = is_ascii_encoding("ascii")
    assert result is True


def test_is_ascii_encoding_utf8():
    """Test that non-ascii encoding returns False."""
    result = is_ascii_encoding("utf-8")
    assert result is False


def test_is_ascii_encoding_invalid():
    """Test that invalid encoding returns False due to LookupError."""
    result = is_ascii_encoding("invalid_encoding")
    assert result is False
