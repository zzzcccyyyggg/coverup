# file: src/click/src/click/_compat.py:300-313
# asked: {"lines": [300, 304, 306, 307, 308, 309, 310, 311, 312], "branches": []}
# gained: {"lines": [300, 304, 306, 307, 308, 309, 310, 311, 312], "branches": []}

import pytest
import io
import typing as t
from click._compat import _force_correct_text_writer, _is_binary_writer, _find_binary_writer


class TestForceCorrectTextWriter:
    def test_force_correct_text_writer_with_binary_writer(self):
        """Test _force_correct_text_writer with a binary writer."""
        binary_writer = io.BytesIO()
        result = _force_correct_text_writer(binary_writer, 'utf-8', 'strict')
        assert hasattr(result, 'write')
        assert _is_binary_writer(binary_writer, False) is True

    def test_force_correct_text_writer_with_text_writer_no_buffer(self):
        """Test _force_correct_text_writer with a text writer that has no buffer."""
        text_writer = io.StringIO()
        result = _force_correct_text_writer(text_writer, 'utf-8', 'strict')
        assert hasattr(result, 'write')
        assert result == text_writer

    def test_force_correct_text_writer_with_text_writer_with_buffer(self):
        """Test _force_correct_text_writer with a text writer that has a buffer."""
        text_writer = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        result = _force_correct_text_writer(text_writer, 'utf-8', 'strict')
        assert hasattr(result, 'write')
        assert _is_binary_writer(text_writer.buffer, True) is True

    def test_force_correct_text_writer_with_force_writable(self):
        """Test _force_correct_text_writer with force_writable=True."""
        binary_writer = io.BytesIO()
        result = _force_correct_text_writer(binary_writer, 'utf-8', 'strict', force_writable=True)
        assert hasattr(result, 'write')
        assert _is_binary_writer(binary_writer, False) is True

    def test_force_correct_text_writer_with_none_encoding_and_errors(self):
        """Test _force_correct_text_writer with None encoding and errors."""
        binary_writer = io.BytesIO()
        result = _force_correct_text_writer(binary_writer, None, None)
        assert hasattr(result, 'write')
        assert _is_binary_writer(binary_writer, False) is True
