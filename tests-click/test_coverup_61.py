# file: src/click/src/click/testing.py:546-577
# asked: {"lines": [546, 547, 548, 562, 563, 564, 566, 567, 569, 571, 572, 574, 575, 576, 577], "branches": [[571, 0], [571, 572]]}
# gained: {"lines": [546, 547, 548, 562, 563, 564, 566, 567, 569, 571, 572, 574, 575, 576, 577], "branches": [[571, 0], [571, 572]]}

import os
import tempfile
import pytest
from click.testing import CliRunner

def test_isolated_filesystem_with_temp_dir():
    """Test isolated_filesystem with temp_dir parameter - should not clean up temp directory"""
    runner = CliRunner()
    
    # Create a temporary directory to use as temp_dir
    with tempfile.TemporaryDirectory() as base_temp_dir:
        original_cwd = os.getcwd()
        
        with runner.isolated_filesystem(temp_dir=base_temp_dir) as temp_path:
            # Verify we're in the new temporary directory
            assert os.getcwd() == temp_path
            assert os.path.exists(temp_path)
            
            # Create a file to verify the filesystem is working
            test_file = os.path.join(temp_path, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")
            assert os.path.exists(test_file)
        
        # After context manager exits, verify we're back to original directory
        assert os.getcwd() == original_cwd
        
        # The temporary directory should still exist since temp_dir was provided
        assert os.path.exists(temp_path)
        assert os.path.exists(os.path.join(temp_path, "test.txt"))

def test_isolated_filesystem_without_temp_dir():
    """Test isolated_filesystem without temp_dir parameter - should clean up temp directory"""
    runner = CliRunner()
    original_cwd = os.getcwd()
    
    with runner.isolated_filesystem() as temp_path:
        # Verify we're in the new temporary directory
        assert os.getcwd() == temp_path
        assert os.path.exists(temp_path)
        
        # Create a file to verify the filesystem is working
        test_file = os.path.join(temp_path, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        assert os.path.exists(test_file)
    
    # After context manager exits, verify we're back to original directory
    assert os.getcwd() == original_cwd
    
    # The temporary directory should be cleaned up since no temp_dir was provided
    assert not os.path.exists(temp_path)

def test_isolated_filesystem_cleanup_failure(monkeypatch):
    """Test isolated_filesystem when cleanup fails (OSError during rmtree)"""
    runner = CliRunner()
    original_cwd = os.getcwd()
    
    # Mock shutil.rmtree to raise OSError to test the exception handling
    import shutil
    def mock_rmtree(path):
        raise OSError("Mocked cleanup failure")
    
    monkeypatch.setattr(shutil, "rmtree", mock_rmtree)
    
    with runner.isolated_filesystem() as temp_path:
        # Verify we're in the new temporary directory
        assert os.getcwd() == temp_path
        assert os.path.exists(temp_path)
    
    # After context manager exits, verify we're back to original directory
    # even though cleanup failed
    assert os.getcwd() == original_cwd
    
    # The test should not raise an exception despite cleanup failure
    # The directory might still exist due to the mocked failure
