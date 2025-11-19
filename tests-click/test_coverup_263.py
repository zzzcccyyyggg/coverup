# file: src/click/src/click/utils.py:192-194
# asked: {"lines": [192, 193, 194], "branches": []}
# gained: {"lines": [192, 193, 194], "branches": []}

import pytest
import tempfile
import os
from click.utils import LazyFile

class TestLazyFileIter:
    def test_lazy_file_iter_with_text_file(self, tmp_path):
        """Test that LazyFile can be iterated over when opened in text mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3")
        
        lazy_file = LazyFile(str(test_file), mode='r', encoding='utf-8')
        
        # This should trigger the __iter__ method and open the file
        lines = list(lazy_file)
        
        assert lines == ["line1\n", "line2\n", "line3"]
        lazy_file.close()

    def test_lazy_file_iter_with_binary_file(self, tmp_path):
        """Test that LazyFile can be iterated over when opened in binary mode."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"line1\nline2\nline3")
        
        lazy_file = LazyFile(str(test_file), mode='rb')
        
        # This should trigger the __iter__ method and open the file
        lines = list(lazy_file)
        
        assert lines == [b"line1\n", b"line2\n", b"line3"]
        lazy_file.close()

    def test_lazy_file_iter_context_manager(self, tmp_path):
        """Test that LazyFile can be iterated over when used as context manager."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3")
        
        with LazyFile(str(test_file), mode='r', encoding='utf-8') as lazy_file:
            lines = list(lazy_file)
            assert lines == ["line1\n", "line2\n", "line3"]
