# file: src/click/src/click/utils.py:358-404
# asked: {"lines": [358, 360, 361, 362, 363, 364, 394, 395, 396, 399, 401, 402, 404], "branches": [[394, 395], [394, 399], [401, 402], [401, 404]]}
# gained: {"lines": [358, 360, 361, 362, 363, 364, 394, 395, 396, 399, 401, 402, 404], "branches": [[394, 395], [394, 399], [401, 402], [401, 404]]}

import os
import tempfile
import pytest
from click.utils import open_file, LazyFile, KeepOpenFile
from click._compat import open_stream


class TestOpenFile:
    def test_open_file_lazy_mode(self, tmp_path):
        """Test open_file with lazy=True parameter."""
        test_file = tmp_path / "test_lazy.txt"
        test_file.write_text("test content")
        
        result = open_file(str(test_file), lazy=True)
        assert isinstance(result, LazyFile)
        assert result.name == str(test_file)
        assert result.mode == "r"
        assert result.encoding is None
        assert result.errors == "strict"
        assert result.atomic is False

    def test_open_file_non_lazy_should_close_false(self, monkeypatch):
        """Test open_file with lazy=False and should_close=False from open_stream."""
        def mock_open_stream(filename, mode, encoding, errors, atomic):
            class MockFile:
                def close(self):
                    pass
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return MockFile(), False
        
        monkeypatch.setattr("click.utils.open_stream", mock_open_stream)
        
        result = open_file("-", lazy=False)
        assert isinstance(result, KeepOpenFile)

    def test_open_file_non_lazy_should_close_true(self, tmp_path):
        """Test open_file with lazy=False and should_close=True from open_stream."""
        test_file = tmp_path / "test_normal.txt"
        test_file.write_text("test content")
        
        result = open_file(str(test_file), lazy=False)
        f, should_close = open_stream(str(test_file), "r")
        assert should_close is True
        result.close()

    def test_open_file_lazy_with_atomic(self, tmp_path):
        """Test open_file with lazy=True and atomic=True."""
        test_file = tmp_path / "test_atomic.txt"
        
        result = open_file(str(test_file), mode="w", lazy=True, atomic=True)
        assert isinstance(result, LazyFile)
        assert result.atomic is True

    def test_open_file_lazy_stdin(self):
        """Test open_file with lazy=True and filename='-' for stdin."""
        result = open_file("-", mode="r", lazy=True)
        assert isinstance(result, LazyFile)
        assert result.name == "-"
        assert result.mode == "r"

    def test_open_file_lazy_stdout(self):
        """Test open_file with lazy=True and filename='-' for stdout."""
        result = open_file("-", mode="w", lazy=True)
        assert isinstance(result, LazyFile)
        assert result.name == "-"
        assert result.mode == "w"
