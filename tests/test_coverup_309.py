# file: src/flask/src/flask/config.py:218-254
# asked: {"lines": [251], "branches": [[250, 251]]}
# gained: {"lines": [251], "branches": [[250, 251]]}

import pytest
import tempfile
import os
from flask import Config
from werkzeug.utils import import_string

class TestConfig:
    def test_from_object_with_string_import(self, monkeypatch):
        """Test that from_object executes line 251 when given a string import path"""
        # Create a mock module with uppercase attributes
        class MockModule:
            TEST_CONFIG = "test_value"
            ANOTHER_CONFIG = 42
            _private = "should_not_be_included"
            lowercase = "should_not_be_included"
        
        # Mock import_string to return our mock module
        def mock_import_string(import_path):
            return MockModule()
        
        monkeypatch.setattr('flask.config.import_string', mock_import_string)
        
        # Create Config with required root_path parameter
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(root_path=tmpdir)
            config.from_object('some.module.path')
            
            # Verify that uppercase attributes were loaded
            assert config['TEST_CONFIG'] == "test_value"
            assert config['ANOTHER_CONFIG'] == 42
            # Verify that private and lowercase attributes were not loaded
            assert '_private' not in config
            assert 'lowercase' not in config
    
    def test_from_object_with_string_import_import_error(self, monkeypatch):
        """Test that from_object handles ImportError when string import fails"""
        def mock_import_string(import_path):
            raise ImportError(f"Could not import '{import_path}'")
        
        monkeypatch.setattr('flask.config.import_string', mock_import_string)
        
        # Create Config with required root_path parameter
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(root_path=tmpdir)
            
            # This should raise ImportError
            with pytest.raises(ImportError):
                config.from_object('nonexistent.module.path')
