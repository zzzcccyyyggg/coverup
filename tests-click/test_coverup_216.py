# file: src/click/src/click/utils.py:146-149
# asked: {"lines": [146, 147, 148, 149], "branches": [[147, 148], [147, 149]]}
# gained: {"lines": [146, 147, 148, 149], "branches": [[147, 148], [147, 149]]}

import pytest
import os
import tempfile
from click.utils import LazyFile

class TestLazyFileRepr:
    def test_repr_opened_file(self):
        """Test __repr__ when file is already opened"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp.flush()
        
        try:
            lazy_file = LazyFile(tmp.name, 'r')
            # Actually open the file to set _f
            lazy_file.open()
            repr_str = repr(lazy_file)
            # The repr should now show the actual file object representation
            assert repr_str.startswith("<_io.TextIOWrapper")
            assert "mode='r'" in repr_str
            assert tmp.name in repr_str
        finally:
            os.unlink(tmp.name)
    
    def test_repr_unopened_file(self):
        """Test __repr__ when file is not yet opened"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp.flush()
        
        try:
            lazy_file = LazyFile(tmp.name, 'w')
            # Ensure file is not opened
            assert lazy_file._f is None
            repr_str = repr(lazy_file)
            expected = f"<unopened file '{tmp.name}' w>"
            assert repr_str == expected
        finally:
            os.unlink(tmp.name)
