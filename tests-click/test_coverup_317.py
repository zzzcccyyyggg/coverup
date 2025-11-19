# file: src/click/src/click/_compat.py:209-215
# asked: {"lines": [209, 215], "branches": []}
# gained: {"lines": [209, 215], "branches": []}

import pytest
from click._compat import _stream_is_misconfigured


class MockStream:
    """A mock stream class that allows setting encoding attribute."""
    def __init__(self, encoding=None):
        self.encoding = encoding


class TestStreamIsMisconfigured:
    def test_stream_with_ascii_encoding(self):
        """Test that a stream with ASCII encoding returns True."""
        stream = MockStream(encoding='ascii')
        assert _stream_is_misconfigured(stream) is True

    def test_stream_with_utf8_encoding(self):
        """Test that a stream with UTF-8 encoding returns False."""
        stream = MockStream(encoding='utf-8')
        assert _stream_is_misconfigured(stream) is False

    def test_stream_with_no_encoding_attribute(self):
        """Test that a stream without encoding attribute returns True (defaults to ASCII)."""
        stream = MockStream()
        delattr(stream, 'encoding')
        assert _stream_is_misconfigured(stream) is True

    def test_stream_with_none_encoding(self):
        """Test that a stream with None encoding returns True (defaults to ASCII)."""
        stream = MockStream(encoding=None)
        assert _stream_is_misconfigured(stream) is True

    def test_stream_with_empty_encoding(self):
        """Test that a stream with empty string encoding returns True (defaults to ASCII)."""
        stream = MockStream(encoding='')
        assert _stream_is_misconfigured(stream) is True
