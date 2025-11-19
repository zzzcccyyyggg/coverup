# file: src/flask/src/flask/config.py:102-124
# asked: {"lines": [102, 114, 115, 116, 117, 118, 119, 124], "branches": [[115, 116], [115, 124], [116, 117], [116, 118]]}
# gained: {"lines": [102, 114, 115, 116, 117, 118, 119, 124], "branches": [[115, 116], [115, 124], [116, 117], [116, 118]]}

import os
import pytest
from flask.config import Config


class TestConfigFromEnvvar:
    def test_from_envvar_success(self, tmp_path, monkeypatch):
        """Test successful loading from environment variable."""
        config_file = tmp_path / "test_config.py"
        config_file.write_text("TEST_VALUE = 'success'")
        
        monkeypatch.setenv("TEST_CONFIG_VAR", str(config_file))
        
        config = Config(root_path=tmp_path)
        result = config.from_envvar("TEST_CONFIG_VAR")
        
        assert result is True
        assert config["TEST_VALUE"] == "success"

    def test_from_envvar_missing_env_var_not_silent(self, tmp_path):
        """Test missing environment variable raises RuntimeError when not silent."""
        config = Config(root_path=tmp_path)
        
        with pytest.raises(RuntimeError) as exc_info:
            config.from_envvar("NONEXISTENT_VAR")
        
        assert "The environment variable 'NONEXISTENT_VAR' is not set" in str(exc_info.value)

    def test_from_envvar_missing_env_var_silent(self, tmp_path, monkeypatch):
        """Test missing environment variable returns False when silent."""
        # Ensure the environment variable is not set
        monkeypatch.delenv("NONEXISTENT_VAR", raising=False)
        
        config = Config(root_path=tmp_path)
        result = config.from_envvar("NONEXISTENT_VAR", silent=True)
        
        assert result is False

    def test_from_envvar_file_not_found_silent(self, tmp_path, monkeypatch):
        """Test file not found returns False when silent."""
        non_existent_file = tmp_path / "nonexistent.py"
        
        monkeypatch.setenv("TEST_CONFIG_VAR", str(non_existent_file))
        
        config = Config(root_path=tmp_path)
        result = config.from_envvar("TEST_CONFIG_VAR", silent=True)
        
        assert result is False

    def test_from_envvar_file_not_found_not_silent(self, tmp_path, monkeypatch):
        """Test file not found raises error when not silent."""
        non_existent_file = tmp_path / "nonexistent.py"
        
        monkeypatch.setenv("TEST_CONFIG_VAR", str(non_existent_file))
        
        config = Config(root_path=tmp_path)
        
        with pytest.raises(OSError):
            config.from_envvar("TEST_CONFIG_VAR", silent=False)
