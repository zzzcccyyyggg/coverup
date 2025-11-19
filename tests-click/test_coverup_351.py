# file: src/click/src/click/utils.py:184-190
# asked: {"lines": [184, 190], "branches": []}
# gained: {"lines": [184, 190], "branches": []}

import pytest
from click.utils import LazyFile
import tempfile
import os

class TestLazyFileExit:
    def test_exit_calls_close_intelligently(self, monkeypatch):
        """Test that __exit__ method calls close_intelligently"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp_path = tmp.name
        
        try:
            lazy_file = LazyFile(tmp_path, 'r')
            
            # Mock close_intelligently to verify it's called
            close_intelligently_called = False
            original_close_intelligently = lazy_file.close_intelligently
            
            def mock_close_intelligently():
                nonlocal close_intelligently_called
                close_intelligently_called = True
                original_close_intelligently()
            
            monkeypatch.setattr(lazy_file, 'close_intelligently', mock_close_intelligently)
            
            # Call __exit__ with various exception scenarios
            # Test with no exception
            lazy_file.__exit__(None, None, None)
            assert close_intelligently_called
            
            # Reset and test with an exception
            close_intelligently_called = False
            lazy_file.__exit__(ValueError, ValueError("test"), None)
            assert close_intelligently_called
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_exit_with_different_exception_types(self, monkeypatch):
        """Test __exit__ with different exception type combinations"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp_path = tmp.name
        
        try:
            lazy_file = LazyFile(tmp_path, 'r')
            
            # Track calls to close_intelligently
            call_count = 0
            original_close_intelligently = lazy_file.close_intelligently
            
            def mock_close_intelligently():
                nonlocal call_count
                call_count += 1
                original_close_intelligently()
            
            monkeypatch.setattr(lazy_file, 'close_intelligently', mock_close_intelligently)
            
            # Test various combinations of exception parameters
            test_cases = [
                (None, None, None),  # No exception
                (ValueError, ValueError("error"), None),  # Exception with value
                (TypeError, None, None),  # Exception type only
                (OSError, OSError("io error"), "traceback_object"),  # All parameters
            ]
            
            for i, (exc_type, exc_value, tb) in enumerate(test_cases, 1):
                lazy_file.__exit__(exc_type, exc_value, tb)
                assert call_count == i  # Should be called exactly i times after i calls
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
