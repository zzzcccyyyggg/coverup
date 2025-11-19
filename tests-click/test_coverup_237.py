# file: src/click/src/click/utils.py:169-172
# asked: {"lines": [169, 171, 172], "branches": [[171, 0], [171, 172]]}
# gained: {"lines": [169, 171, 172], "branches": [[171, 0], [171, 172]]}

import pytest
import tempfile
import os
from click.utils import LazyFile

class TestLazyFileClose:
    def test_close_with_file_none(self):
        """Test that close() does nothing when _f is None"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp_name = tmp.name
        
        try:
            lazy_file = LazyFile(tmp_name, 'r')
            # Ensure _f is None (file not opened yet)
            assert lazy_file._f is None
            # This should not raise any exception
            lazy_file.close()
            # Verify _f is still None
            assert lazy_file._f is None
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def test_close_with_file_open(self):
        """Test that close() actually closes the file when _f is not None"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp_name = tmp.name
        
        try:
            lazy_file = LazyFile(tmp_name, 'r')
            # Open the file to set _f
            lazy_file.open()
            assert lazy_file._f is not None
            # Close should work without errors
            lazy_file.close()
            # After close, the file should be closed (check closed attribute)
            assert lazy_file._f.closed
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
