# file: src/flask/src/flask/cli.py:493-512
# asked: {"lines": [493, 496, 497, 498, 501, 502, 503, 504, 505, 506, 509, 510, 512], "branches": [[501, 502], [501, 509], [509, 510], [509, 512]]}
# gained: {"lines": [493, 496, 497, 498, 501, 502, 503, 504, 505, 506, 509, 510, 512], "branches": [[501, 502], [501, 509], [509, 510], [509, 512]]}

import pytest
import click
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import os


class TestEnvFileCallback:
    """Test cases for _env_file_callback function to achieve full coverage."""
    
    def test_env_file_callback_dotenv_not_installed_with_value(self):
        """Test _env_file_callback when dotenv is not installed and value is provided."""
        runner = CliRunner()
        
        with patch.dict('sys.modules', {'dotenv': None}):
            with pytest.raises(click.BadParameter) as exc_info:
                ctx = MagicMock()
                ctx.obj.load_dotenv_defaults = False
                
                from flask.cli import _env_file_callback
                _env_file_callback(ctx, MagicMock(), "test.env")
            
            assert "python-dotenv must be installed to load an env file." in str(exc_info.value)
    
    def test_env_file_callback_dotenv_not_installed_no_value(self):
        """Test _env_file_callback when dotenv is not installed and no value is provided."""
        runner = CliRunner()
        
        with patch.dict('sys.modules', {'dotenv': None}):
            ctx = MagicMock()
            ctx.obj.load_dotenv_defaults = False
            
            from flask.cli import _env_file_callback
            result = _env_file_callback(ctx, MagicMock(), None)
            
            assert result is None
    
    def test_env_file_callback_dotenv_installed_with_value(self):
        """Test _env_file_callback when dotenv is installed and value is provided."""
        runner = CliRunner()
        
        with patch('flask.cli.load_dotenv') as mock_load_dotenv:
            ctx = MagicMock()
            ctx.obj.load_dotenv_defaults = False
            
            from flask.cli import _env_file_callback
            result = _env_file_callback(ctx, MagicMock(), "test.env")
            
            mock_load_dotenv.assert_called_once_with("test.env", load_defaults=False)
            assert result == "test.env"
    
    def test_env_file_callback_dotenv_installed_no_value_but_load_defaults(self):
        """Test _env_file_callback when dotenv is installed, no value but load_defaults is True."""
        runner = CliRunner()
        
        with patch('flask.cli.load_dotenv') as mock_load_dotenv:
            ctx = MagicMock()
            ctx.obj.load_dotenv_defaults = True
            
            from flask.cli import _env_file_callback
            result = _env_file_callback(ctx, MagicMock(), None)
            
            mock_load_dotenv.assert_called_once_with(None, load_defaults=True)
            assert result is None
    
    def test_env_file_callback_dotenv_installed_with_value_and_load_defaults(self):
        """Test _env_file_callback when dotenv is installed, value provided and load_defaults is True."""
        runner = CliRunner()
        
        with patch('flask.cli.load_dotenv') as mock_load_dotenv:
            ctx = MagicMock()
            ctx.obj.load_dotenv_defaults = True
            
            from flask.cli import _env_file_callback
            result = _env_file_callback(ctx, MagicMock(), "custom.env")
            
            mock_load_dotenv.assert_called_once_with("custom.env", load_defaults=True)
            assert result == "custom.env"
