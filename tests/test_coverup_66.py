# file: src/flask/src/flask/config.py:187-216
# asked: {"lines": [187, 188, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216], "branches": [[211, 212], [211, 213]]}
# gained: {"lines": [187, 188, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216], "branches": [[211, 212], [211, 213]]}

import pytest
import tempfile
import os
import errno
from flask import Config

class TestConfigFromPyfile:
    def test_from_pyfile_success(self, tmp_path):
        """Test successful loading of a Python config file."""
        config_content = """
DEBUG = True
SECRET_KEY = 'test-secret'
DATABASE_URI = 'sqlite:///test.db'
"""
        config_file = tmp_path / "test_config.py"
        config_file.write_text(config_content)
        
        cfg = Config(root_path=str(tmp_path))
        result = cfg.from_pyfile("test_config.py")
        
        assert result is True
        assert cfg["DEBUG"] is True
        assert cfg["SECRET_KEY"] == "test-secret"
        assert cfg["DATABASE_URI"] == "sqlite:///test.db"

    def test_from_pyfile_file_not_found_silent(self, tmp_path):
        """Test silent failure when file doesn't exist and silent=True."""
        cfg = Config(root_path=str(tmp_path))
        result = cfg.from_pyfile("nonexistent.py", silent=True)
        
        assert result is False
        assert len(cfg) == 0

    def test_from_pyfile_file_not_found_not_silent(self, tmp_path):
        """Test exception when file doesn't exist and silent=False."""
        cfg = Config(root_path=str(tmp_path))
        
        with pytest.raises(OSError) as exc_info:
            cfg.from_pyfile("nonexistent.py", silent=False)
        
        assert "Unable to load configuration file" in str(exc_info.value)
        assert exc_info.value.errno == errno.ENOENT

    def test_from_pyfile_is_directory_silent(self, tmp_path):
        """Test silent failure when path is a directory and silent=True."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        cfg = Config(root_path=str(tmp_path))
        result = cfg.from_pyfile("subdir", silent=True)
        
        assert result is False
        assert len(cfg) == 0

    def test_from_pyfile_is_directory_not_silent(self, tmp_path):
        """Test exception when path is a directory and silent=False."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        cfg = Config(root_path=str(tmp_path))
        
        with pytest.raises(OSError) as exc_info:
            cfg.from_pyfile("subdir", silent=False)
        
        assert "Unable to load configuration file" in str(exc_info.value)
        assert exc_info.value.errno == errno.EISDIR

    def test_from_pyfile_not_directory_silent(self, tmp_path):
        """Test silent failure when path component is not a directory and silent=True."""
        # Create a file that will be treated as a directory in the path
        some_file = tmp_path / "some_file"
        some_file.write_text("content")
        
        cfg = Config(root_path=str(tmp_path))
        result = cfg.from_pyfile("some_file/nested.py", silent=True)
        
        assert result is False
        assert len(cfg) == 0

    def test_from_pyfile_not_directory_not_silent(self, tmp_path):
        """Test exception when path component is not a directory and silent=False."""
        # Create a file that will be treated as a directory in the path
        some_file = tmp_path / "some_file"
        some_file.write_text("content")
        
        cfg = Config(root_path=str(tmp_path))
        
        with pytest.raises(OSError) as exc_info:
            cfg.from_pyfile("some_file/nested.py", silent=False)
        
        assert "Unable to load configuration file" in str(exc_info.value)
        assert exc_info.value.errno == errno.ENOTDIR

    def test_from_pyfile_with_relative_path(self, tmp_path):
        """Test loading config file with relative path."""
        config_content = "TEST_VALUE = 42"
        config_file = tmp_path / "config" / "settings.py"
        config_file.parent.mkdir()
        config_file.write_text(config_content)
        
        cfg = Config(root_path=str(tmp_path))
        result = cfg.from_pyfile("config/settings.py")
        
        assert result is True
        assert cfg["TEST_VALUE"] == 42

    def test_from_pyfile_with_complex_config(self, tmp_path):
        """Test loading config file with complex Python code."""
        config_content = """
def get_database_url():
    return "postgresql://localhost/testdb"

DATABASE_URL = get_database_url()
MAX_CONNECTIONS = 100
ENVIRONMENT = "testing"
"""
        config_file = tmp_path / "complex_config.py"
        config_file.write_text(config_content)
        
        cfg = Config(root_path=str(tmp_path))
        result = cfg.from_pyfile("complex_config.py")
        
        assert result is True
        assert cfg["DATABASE_URL"] == "postgresql://localhost/testdb"
        assert cfg["MAX_CONNECTIONS"] == 100
        assert cfg["ENVIRONMENT"] == "testing"
