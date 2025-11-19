# file: src/flask/src/flask/config.py:94-100
# asked: {"lines": [94, 97, 99, 100], "branches": []}
# gained: {"lines": [94, 97, 99, 100], "branches": []}

import os
import pytest
from flask.config import Config

class TestConfigInit:
    """Test cases for Config.__init__ method to achieve full coverage."""
    
    def test_init_with_defaults(self):
        """Test Config initialization with defaults parameter."""
        root_path = "/test/path"
        defaults = {"DEBUG": True, "SECRET_KEY": "test_key"}
        
        config = Config(root_path, defaults=defaults)
        
        assert config.root_path == root_path
        assert config["DEBUG"] is True
        assert config["SECRET_KEY"] == "test_key"
    
    def test_init_without_defaults(self):
        """Test Config initialization without defaults parameter."""
        root_path = "/test/path"
        
        config = Config(root_path)
        
        assert config.root_path == root_path
        assert config == {}
    
    def test_init_with_none_defaults(self):
        """Test Config initialization with None defaults parameter."""
        root_path = "/test/path"
        
        config = Config(root_path, defaults=None)
        
        assert config.root_path == root_path
        assert config == {}
