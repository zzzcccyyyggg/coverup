# file: src/click/src/click/utils.py:151-167
# asked: {"lines": [151, 156, 157, 158, 159, 160, 162, 163, 165, 166, 167], "branches": [[156, 157], [156, 158]]}
# gained: {"lines": [151, 156, 158, 159, 160, 162, 163, 165, 166, 167], "branches": [[156, 158]]}

import pytest
import tempfile
import os
from click.utils import LazyFile
from click.exceptions import FileError

class TestLazyFileOpen:
    def test_open_already_open_file(self):
        """Test that open() returns the already open file object when _f is not None."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write('test content')
            tmp.flush()
        
        try:
            lazy_file = LazyFile(tmp.name, 'r')
            # Force the file to be opened by accessing it
            _ = lazy_file._f
            # Now _f should not be None, so open() should return it directly
            result = lazy_file.open()
            assert result is lazy_file._f
        finally:
            os.unlink(tmp.name)

    def test_open_with_oserror_raises_fileerror(self):
        """Test that open() raises FileError when open_stream raises OSError."""
        # Create a directory path to simulate permission error
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file path that points to a directory (will cause OSError)
            dir_file_path = os.path.join(tmpdir, 'test_file')
            os.makedirs(dir_file_path, exist_ok=True)
            
            lazy_file = LazyFile(dir_file_path, 'w')
            
            with pytest.raises(FileError) as exc_info:
                lazy_file.open()
            
            assert exc_info.value.filename == dir_file_path
            # FileError stores the hint as the message, not as a separate attribute
            assert exc_info.value.message is not None

    def test_open_successful_first_time(self):
        """Test that open() successfully opens a file when _f is None."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write('test content')
            tmp.flush()
        
        try:
            lazy_file = LazyFile(tmp.name, 'r')
            # Ensure _f is None initially
            assert lazy_file._f is None
            
            # Call open() which should open the file
            result = lazy_file.open()
            
            # Verify the file was opened and stored in _f
            assert result is lazy_file._f
            assert lazy_file._f is not None
            # Verify we can read from the file
            content = lazy_file._f.read()
            assert content == 'test content'
        finally:
            os.unlink(tmp.name)
