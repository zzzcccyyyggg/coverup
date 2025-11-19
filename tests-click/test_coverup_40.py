# file: src/click/src/click/utils.py:116-141
# asked: {"lines": [116, 119, 120, 121, 122, 124, 125, 126, 127, 128, 129, 130, 132, 133, 135, 139, 140, 141], "branches": [[132, 133], [132, 135], [135, 139], [135, 140]]}
# gained: {"lines": [116, 119, 120, 121, 122, 124, 125, 126, 127, 128, 129, 130, 132, 133, 135, 139, 140, 141], "branches": [[132, 133], [132, 135], [135, 139], [135, 140]]}

import pytest
import os
import tempfile
from click.utils import LazyFile

class TestLazyFile:
    def test_lazy_file_init_with_stdin(self, monkeypatch):
        """Test LazyFile initialization with '-' filename (stdin/stdout)"""
        mock_stream = object()
        mock_should_close = True
        
        def mock_open_stream(filename, mode, encoding, errors):
            return mock_stream, mock_should_close
            
        monkeypatch.setattr('click.utils.open_stream', mock_open_stream)
        
        lazy_file = LazyFile('-', 'r')
        
        assert lazy_file.name == '-'
        assert lazy_file.mode == 'r'
        assert lazy_file._f is mock_stream
        assert lazy_file.should_close == mock_should_close
        assert lazy_file.encoding is None
        assert lazy_file.errors == 'strict'
        assert lazy_file.atomic is False

    def test_lazy_file_init_with_read_mode(self):
        """Test LazyFile initialization with read mode on regular file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write('test content')
            tmp_path = tmp.name
            
        try:
            lazy_file = LazyFile(tmp_path, 'r')
            
            assert lazy_file.name == tmp_path
            assert lazy_file.mode == 'r'
            assert lazy_file._f is None
            assert lazy_file.should_close is True
            assert lazy_file.encoding is None
            assert lazy_file.errors == 'strict'
            assert lazy_file.atomic is False
        finally:
            os.unlink(tmp_path)

    def test_lazy_file_init_with_read_mode_and_encoding(self):
        """Test LazyFile initialization with read mode and encoding"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write('test content')
            tmp_path = tmp.name
            
        try:
            lazy_file = LazyFile(tmp_path, 'r', encoding='utf-8', errors='ignore')
            
            assert lazy_file.name == tmp_path
            assert lazy_file.mode == 'r'
            assert lazy_file._f is None
            assert lazy_file.should_close is True
            assert lazy_file.encoding == 'utf-8'
            assert lazy_file.errors == 'ignore'
            assert lazy_file.atomic is False
        finally:
            os.unlink(tmp_path)

    def test_lazy_file_init_with_write_mode(self):
        """Test LazyFile initialization with write mode (no early file open)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test_file.txt')
            
            lazy_file = LazyFile(file_path, 'w')
            
            assert lazy_file.name == file_path
            assert lazy_file.mode == 'w'
            assert lazy_file._f is None
            assert lazy_file.should_close is True
            assert lazy_file.encoding is None
            assert lazy_file.errors == 'strict'
            assert lazy_file.atomic is False

    def test_lazy_file_init_with_atomic_flag(self):
        """Test LazyFile initialization with atomic flag"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test_file.txt')
            
            lazy_file = LazyFile(file_path, 'w', atomic=True)
            
            assert lazy_file.name == file_path
            assert lazy_file.mode == 'w'
            assert lazy_file._f is None
            assert lazy_file.should_close is True
            assert lazy_file.encoding is None
            assert lazy_file.errors == 'strict'
            assert lazy_file.atomic is True
