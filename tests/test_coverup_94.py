# file: src/flask/src/flask/config.py:256-302
# asked: {"lines": [256, 260, 261, 290, 292, 293, 294, 295, 296, 297, 299, 300, 302], "branches": [[296, 297], [296, 299]]}
# gained: {"lines": [256, 260, 261, 290, 292, 293, 294, 295, 296, 297, 299, 300, 302], "branches": [[296, 297], [296, 299]]}

import pytest
import tempfile
import os
import errno
from unittest.mock import Mock, patch
import json

class TestConfigFromFile:
    """Test cases for Config.from_file method to achieve full coverage."""
    
    def test_from_file_success_text_mode(self):
        """Test successful file loading in text mode."""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(root_path=temp_dir)
            
            # Create a temporary config file
            temp_filename = os.path.join(temp_dir, 'config.json')
            with open(temp_filename, 'w') as f:
                json.dump({'TEST_KEY': 'test_value'}, f)
            
            result = config.from_file('config.json', load=json.load)
            assert result is True
            assert config['TEST_KEY'] == 'test_value'
    
    def test_from_file_success_binary_mode(self):
        """Test successful file loading in binary mode."""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(root_path=temp_dir)
            
            # Create a temporary config file
            temp_filename = os.path.join(temp_dir, 'config.bin')
            with open(temp_filename, 'wb') as f:
                # Use a simple binary format - pickle for example
                import pickle
                pickle.dump({'BINARY_KEY': 'binary_value'}, f)
            
            def binary_load(file_obj):
                import pickle
                return pickle.load(file_obj)
            
            result = config.from_file('config.bin', load=binary_load, text=False)
            assert result is True
            assert config['BINARY_KEY'] == 'binary_value'
    
    def test_from_file_file_not_found_silent(self):
        """Test file not found with silent=True returns False."""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(root_path=temp_dir)
            result = config.from_file('nonexistent_file.json', load=json.load, silent=True)
            assert result is False
    
    def test_from_file_file_not_found_not_silent(self):
        """Test file not found with silent=False raises OSError."""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(root_path=temp_dir)
            
            with pytest.raises(OSError) as exc_info:
                config.from_file('nonexistent_file.json', load=json.load, silent=False)
            
            assert "Unable to load configuration file" in str(exc_info.value)
    
    def test_from_file_is_directory_silent(self):
        """Test when path is a directory with silent=True returns False."""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(root_path=temp_dir)
            
            # Create a subdirectory
            subdir = os.path.join(temp_dir, 'subdir')
            os.makedirs(subdir)
            
            result = config.from_file('subdir', load=json.load, silent=True)
            assert result is False
    
    def test_from_file_is_directory_not_silent(self):
        """Test when path is a directory with silent=False raises OSError."""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(root_path=temp_dir)
            
            # Create a subdirectory
            subdir = os.path.join(temp_dir, 'subdir')
            os.makedirs(subdir)
            
            with pytest.raises(OSError) as exc_info:
                config.from_file('subdir', load=json.load, silent=False)
            
            assert "Unable to load configuration file" in str(exc_info.value)
    
    def test_from_file_other_os_error(self):
        """Test other OSError types are re-raised with modified message."""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(root_path=temp_dir)
            
            # Mock open to raise a different OSError (not ENOENT or EISDIR)
            with patch('builtins.open') as mock_open:
                mock_open.side_effect = OSError(errno.EPERM, "Permission denied")
                
                with pytest.raises(OSError) as exc_info:
                    config.from_file('some_file.json', load=json.load, silent=True)
                
                assert "Unable to load configuration file" in str(exc_info.value)
                assert "Permission denied" in str(exc_info.value)
