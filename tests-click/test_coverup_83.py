# file: src/click/src/click/_compat.py:56-79
# asked: {"lines": [56, 57, 62, 63, 66, 67, 69, 71, 72, 73, 74, 75, 77, 79], "branches": []}
# gained: {"lines": [56, 57, 62, 63, 66, 67, 69, 71, 72, 73, 74, 75, 77, 79], "branches": []}

import pytest
import io
import typing as t
from click._compat import _NonClosingTextIOWrapper, _FixupStream


class TestNonClosingTextIOWrapper:
    def test_init_with_force_flags(self):
        """Test initialization with force_readable and force_writable flags."""
        binary_stream = io.BytesIO(b"test data")
        wrapper = _NonClosingTextIOWrapper(
            binary_stream,
            encoding="utf-8",
            errors="strict",
            force_readable=True,
            force_writable=True
        )
        
        assert wrapper._stream._force_readable is True
        assert wrapper._stream._force_writable is True
        assert isinstance(wrapper._stream, _FixupStream)

    def test_del_successful_detach(self):
        """Test __del__ method when detach succeeds."""
        binary_stream = io.BytesIO(b"test data")
        wrapper = _NonClosingTextIOWrapper(
            binary_stream,
            encoding="utf-8",
            errors="strict"
        )
        
        # Manually call __del__ to test the detach logic
        wrapper.__del__()
        
        # Verify the stream is still accessible after detach
        assert wrapper._stream is not None

    def test_del_detach_exception(self):
        """Test __del__ method when detach raises an exception."""
        binary_stream = io.BytesIO(b"test data")
        wrapper = _NonClosingTextIOWrapper(
            binary_stream,
            encoding="utf-8",
            errors="strict"
        )
        
        # Mock detach to raise an exception
        original_detach = wrapper.detach
        
        def mock_detach():
            raise Exception("Detach failed")
        
        wrapper.detach = mock_detach
        
        # This should not raise an exception due to the try/except block
        wrapper.__del__()
        
        # Restore original method
        wrapper.detach = original_detach

    def test_isatty_with_stream_isatty(self, monkeypatch):
        """Test isatty method delegates to underlying stream's isatty."""
        binary_stream = io.BytesIO(b"test data")
        wrapper = _NonClosingTextIOWrapper(
            binary_stream,
            encoding="utf-8",
            errors="strict"
        )
        
        # Mock the underlying stream's isatty method
        was_called = False
        
        def mock_isatty():
            nonlocal was_called
            was_called = True
            return True
        
        monkeypatch.setattr(wrapper._stream, "isatty", mock_isatty)
        
        result = wrapper.isatty()
        
        assert was_called is True
        assert result is True

    def test_isatty_with_stream_isatty_false(self, monkeypatch):
        """Test isatty method when underlying stream returns False."""
        binary_stream = io.BytesIO(b"test data")
        wrapper = _NonClosingTextIOWrapper(
            binary_stream,
            encoding="utf-8",
            errors="strict"
        )
        
        # Mock the underlying stream's isatty method to return False
        def mock_isatty():
            return False
        
        monkeypatch.setattr(wrapper._stream, "isatty", mock_isatty)
        
        result = wrapper.isatty()
        
        assert result is False
