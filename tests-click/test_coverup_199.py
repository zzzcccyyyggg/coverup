# file: src/click/src/click/_compat.py:92-100
# asked: {"lines": [92, 95, 96, 98, 99, 100], "branches": []}
# gained: {"lines": [92, 95, 96, 98, 99, 100], "branches": []}

import pytest
import typing as t
from io import BytesIO
from click._compat import _FixupStream


class TestFixupStream:
    def test_init_with_defaults(self):
        """Test _FixupStream initialization with default parameters."""
        stream = BytesIO(b"test data")
        fixup_stream = _FixupStream(stream)
        
        assert fixup_stream._stream is stream
        assert fixup_stream._force_readable is False
        assert fixup_stream._force_writable is False

    def test_init_with_force_readable(self):
        """Test _FixupStream initialization with force_readable=True."""
        stream = BytesIO(b"test data")
        fixup_stream = _FixupStream(stream, force_readable=True)
        
        assert fixup_stream._stream is stream
        assert fixup_stream._force_readable is True
        assert fixup_stream._force_writable is False

    def test_init_with_force_writable(self):
        """Test _FixupStream initialization with force_writable=True."""
        stream = BytesIO(b"test data")
        fixup_stream = _FixupStream(stream, force_writable=True)
        
        assert fixup_stream._stream is stream
        assert fixup_stream._force_readable is False
        assert fixup_stream._force_writable is True

    def test_init_with_both_forced(self):
        """Test _FixupStream initialization with both force flags set to True."""
        stream = BytesIO(b"test data")
        fixup_stream = _FixupStream(stream, force_readable=True, force_writable=True)
        
        assert fixup_stream._stream is stream
        assert fixup_stream._force_readable is True
        assert fixup_stream._force_writable is True
