# file: src/click/src/click/_compat.py:48-53
# asked: {"lines": [48, 50, 51, 52, 53], "branches": [[51, 52], [51, 53]]}
# gained: {"lines": [48, 50, 51, 52, 53], "branches": [[51, 52], [51, 53]]}

import pytest
import sys
import typing as t
from click._compat import get_best_encoding, is_ascii_encoding


class MockStream:
    def __init__(self, encoding=None):
        self.encoding = encoding


def test_get_best_encoding_with_ascii_encoding():
    """Test get_best_encoding when stream has ASCII encoding."""
    stream = MockStream(encoding='ascii')
    result = get_best_encoding(stream)
    assert result == 'utf-8'


def test_get_best_encoding_with_non_ascii_encoding():
    """Test get_best_encoding when stream has non-ASCII encoding."""
    stream = MockStream(encoding='utf-16')
    result = get_best_encoding(stream)
    assert result == 'utf-16'


def test_get_best_encoding_no_encoding_attribute():
    """Test get_best_encoding when stream has no encoding attribute."""
    stream = object()
    result = get_best_encoding(stream)
    assert result == sys.getdefaultencoding()


def test_get_best_encoding_none_encoding():
    """Test get_best_encoding when stream encoding is None."""
    stream = MockStream(encoding=None)
    result = get_best_encoding(stream)
    assert result == sys.getdefaultencoding()
