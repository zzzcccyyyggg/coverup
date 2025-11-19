# file: src/click/src/click/testing.py:131-148
# asked: {"lines": [131, 135, 136, 138, 139, 141, 143, 144, 145, 146, 148], "branches": [[135, 136], [135, 143], [138, 139], [138, 141], [143, 144], [143, 145], [145, 146], [145, 148]]}
# gained: {"lines": [131, 135, 136, 138, 141, 143, 144, 145, 146, 148], "branches": [[135, 136], [135, 143], [138, 141], [143, 144], [143, 145], [145, 146], [145, 148]]}

import io
import pytest
import typing as t
from click.testing import make_input_stream


class MockStreamWithoutBinaryReader:
    """A mock stream that has a read method but no binary reader."""
    def read(self, size=-1):
        return b""


def test_make_input_stream_with_stream_no_binary_reader(monkeypatch):
    """Test make_input_stream with a stream that has no binary reader."""
    mock_stream = MockStreamWithoutBinaryReader()
    
    # Mock _find_binary_reader to return None to trigger the TypeError
    def mock_find_binary_reader(stream):
        return None
    
    monkeypatch.setattr('click.testing._find_binary_reader', mock_find_binary_reader)
    
    with pytest.raises(TypeError, match="Could not find binary reader for input stream."):
        make_input_stream(mock_stream, "utf-8")


def test_make_input_stream_with_none():
    """Test make_input_stream with None input."""
    result = make_input_stream(None, "utf-8")
    assert isinstance(result, io.BytesIO)
    assert result.read() == b""


def test_make_input_stream_with_string():
    """Test make_input_stream with string input."""
    test_string = "hello world"
    result = make_input_stream(test_string, "utf-8")
    assert isinstance(result, io.BytesIO)
    assert result.read() == test_string.encode("utf-8")


def test_make_input_stream_with_bytes():
    """Test make_input_stream with bytes input."""
    test_bytes = b"hello bytes"
    result = make_input_stream(test_bytes, "utf-8")
    assert isinstance(result, io.BytesIO)
    assert result.read() == test_bytes
