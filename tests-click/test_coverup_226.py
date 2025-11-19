# file: src/click/src/click/utils.py:174-179
# asked: {"lines": [174, 178, 179], "branches": [[178, 0], [178, 179]]}
# gained: {"lines": [174, 178, 179], "branches": [[178, 0], [178, 179]]}

import pytest
import tempfile
import os
from click.utils import LazyFile

class TestLazyFileCloseIntelligently:
    
    def test_close_intelligently_should_close_true(self):
        """Test that close_intelligently calls close when should_close is True"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp_path = tmp.name
        
        try:
            lazy_file = LazyFile(tmp_path, 'r')
            # Ensure file is opened
            lazy_file.open()
            assert lazy_file.should_close is True
            assert lazy_file._f is not None
            assert not lazy_file._f.closed
            
            # Call close_intelligently - should close the file
            lazy_file.close_intelligently()
            
            # Verify file was closed
            assert lazy_file._f.closed
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_close_intelligently_should_close_false(self):
        """Test that close_intelligently does not call close when should_close is False"""
        # Create a LazyFile for stdin (which has should_close=False)
        lazy_file = LazyFile('-', 'r')
        # Ensure file is opened
        lazy_file.open()
        assert lazy_file.should_close is False
        assert lazy_file._f is not None
        original_closed_state = lazy_file._f.closed
        
        # Call close_intelligently - should NOT close the file
        lazy_file.close_intelligently()
        
        # Verify file was NOT closed (state unchanged)
        assert lazy_file._f.closed == original_closed_state
