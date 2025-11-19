# file: src/click/src/click/_compat.py:284-297
# asked: {"lines": [284, 288, 290, 291, 292, 293, 294, 295, 296], "branches": []}
# gained: {"lines": [284, 288, 290, 291, 292, 293, 294, 295, 296], "branches": []}

import pytest
import typing as t
from io import BytesIO, StringIO
from click._compat import _force_correct_text_reader, _is_binary_reader, _find_binary_reader, _force_correct_text_stream

class TestForceCorrectTextReader:
    
    def test_force_correct_text_reader_with_binary_stream(self):
        """Test _force_correct_text_reader with a binary stream."""
        binary_stream = BytesIO(b"test data")
        result = _force_correct_text_reader(binary_stream, "utf-8", "replace")
        assert hasattr(result, "read")
        assert hasattr(result, "encoding")
        assert result.encoding == "utf-8"
    
    def test_force_correct_text_reader_with_text_stream_force_readable(self):
        """Test _force_correct_text_reader with a text stream and force_readable=True."""
        text_stream = StringIO("test data")
        result = _force_correct_text_reader(text_stream, "utf-8", "replace", force_readable=True)
        assert hasattr(result, "read")
        assert hasattr(result, "encoding")
    
    def test_force_correct_text_reader_with_text_stream_no_force_readable(self):
        """Test _force_correct_text_reader with a text stream and force_readable=False."""
        text_stream = StringIO("test data")
        result = _force_correct_text_reader(text_stream, "utf-8", "replace", force_readable=False)
        assert hasattr(result, "read")
        assert hasattr(result, "encoding")
    
    def test_force_correct_text_reader_with_none_encoding_errors(self):
        """Test _force_correct_text_reader with None encoding and errors."""
        binary_stream = BytesIO(b"test data")
        result = _force_correct_text_reader(binary_stream, None, None)
        assert hasattr(result, "read")
        assert hasattr(result, "encoding")
