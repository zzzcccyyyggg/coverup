# file: src/flask/src/flask/cli.py:698-763
# asked: {"lines": [698, 699, 732, 733, 734, 735, 736, 737, 739, 740, 743, 745, 747, 748, 749, 750, 752, 754, 755, 757, 758, 759, 761, 763], "branches": [[735, 736], [735, 743], [747, 748], [747, 754], [748, 749], [748, 754], [749, 750], [749, 752], [754, 755], [754, 757], [757, 758], [757, 763], [758, 759], [758, 761]]}
# gained: {"lines": [698, 699, 732, 733, 734, 735, 736, 737, 739, 740, 743, 745, 747, 748, 749, 750, 752, 754, 755, 757, 758, 759, 761, 763], "branches": [[735, 736], [735, 743], [747, 748], [747, 754], [748, 749], [748, 754], [749, 750], [749, 752], [754, 755], [754, 757], [757, 758], [757, 763], [758, 759], [758, 761]]}

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
import flask.cli

def test_load_dotenv_no_dotenv_installed_with_env_files(monkeypatch):
    """Test load_dotenv when python-dotenv is not installed and env files exist."""
    # Mock ImportError for dotenv
    with patch.dict('sys.modules', {'dotenv': None}):
        # Create temporary .env and .flaskenv files
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, '.env')
            flaskenv_file = os.path.join(tmpdir, '.flaskenv')
            
            with open(env_file, 'w') as f:
                f.write('TEST_VAR=value')
            with open(flaskenv_file, 'w') as f:
                f.write('FLASK_VAR=flask_value')
            
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Mock click.secho to capture the warning message
                mock_secho = MagicMock()
                monkeypatch.setattr('flask.cli.click.secho', mock_secho)
                
                # Test with path parameter
                result = flask.cli.load_dotenv(path=env_file)
                assert result is False
                mock_secho.assert_called_once()
                
                # Reset mock and test without path but with existing files
                mock_secho.reset_mock()
                result = flask.cli.load_dotenv(path=None)
                assert result is False
                mock_secho.assert_called_once()
                
            finally:
                os.chdir(original_cwd)

def test_load_dotenv_no_dotenv_installed_no_env_files():
    """Test load_dotenv when python-dotenv is not installed and no env files exist."""
    with patch.dict('sys.modules', {'dotenv': None}):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Ensure no .env or .flaskenv files exist
                assert not os.path.isfile('.env')
                assert not os.path.isfile('.flaskenv')
                
                result = flask.cli.load_dotenv(path=None)
                assert result is False
                
                result = flask.cli.load_dotenv(path='/nonexistent/file')
                assert result is False
                
            finally:
                os.chdir(original_cwd)

def test_load_dotenv_with_dotenv_and_default_files(monkeypatch):
    """Test load_dotenv with python-dotenv installed and default files."""
    mock_dotenv = MagicMock()
    mock_dotenv.find_dotenv.side_effect = lambda name, usecwd: f'./{name}' if name in ['.flaskenv', '.env'] else None
    mock_dotenv.dotenv_values.return_value = {'TEST_VAR': 'test_value', 'ANOTHER_VAR': 'another_value'}
    
    with patch.dict('sys.modules', {'dotenv': mock_dotenv}):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Create mock env files
                env_file = os.path.join(tmpdir, '.env')
                flaskenv_file = os.path.join(tmpdir, '.flaskenv')
                with open(env_file, 'w') as f:
                    f.write('TEST_VAR=value')
                with open(flaskenv_file, 'w') as f:
                    f.write('FLASK_VAR=flask_value')
                
                # Clear any existing env vars we'll test
                if 'TEST_VAR' in os.environ:
                    monkeypatch.delenv('TEST_VAR')
                if 'ANOTHER_VAR' in os.environ:
                    monkeypatch.delenv('ANOTHER_VAR')
                
                result = flask.cli.load_dotenv(load_defaults=True)
                assert result is True
                assert mock_dotenv.find_dotenv.call_count == 2
                assert mock_dotenv.dotenv_values.call_count == 2
                assert os.environ['TEST_VAR'] == 'test_value'
                assert os.environ['ANOTHER_VAR'] == 'another_value'
                
            finally:
                os.chdir(original_cwd)
                # Clean up env vars
                if 'TEST_VAR' in os.environ:
                    monkeypatch.delenv('TEST_VAR')
                if 'ANOTHER_VAR' in os.environ:
                    monkeypatch.delenv('ANOTHER_VAR')

def test_load_dotenv_with_custom_path(monkeypatch):
    """Test load_dotenv with a custom path parameter."""
    mock_dotenv = MagicMock()
    mock_dotenv.find_dotenv.return_value = None  # No default files found
    mock_dotenv.dotenv_values.return_value = {'CUSTOM_VAR': 'custom_value'}
    
    with patch.dict('sys.modules', {'dotenv': mock_dotenv}):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_env_file = os.path.join(tmpdir, 'custom.env')
            with open(custom_env_file, 'w') as f:
                f.write('CUSTOM_VAR=custom_value')
            
            # Clear any existing env var
            if 'CUSTOM_VAR' in os.environ:
                monkeypatch.delenv('CUSTOM_VAR')
            
            result = flask.cli.load_dotenv(path=custom_env_file, load_defaults=False)
            assert result is True
            mock_dotenv.dotenv_values.assert_called_once_with(custom_env_file, encoding='utf-8')
            assert os.environ['CUSTOM_VAR'] == 'custom_value'
            
            # Clean up
            if 'CUSTOM_VAR' in os.environ:
                monkeypatch.delenv('CUSTOM_VAR')

def test_load_dotenv_with_nonexistent_path(monkeypatch):
    """Test load_dotenv with a nonexistent custom path."""
    mock_dotenv = MagicMock()
    mock_dotenv.find_dotenv.return_value = None
    
    with patch.dict('sys.modules', {'dotenv': mock_dotenv}):
        result = flask.cli.load_dotenv(path='/nonexistent/file.env', load_defaults=False)
        assert result is False
        mock_dotenv.dotenv_values.assert_not_called()

def test_load_dotenv_skip_existing_env_vars(monkeypatch):
    """Test that existing environment variables are not overwritten."""
    mock_dotenv = MagicMock()
    mock_dotenv.find_dotenv.return_value = './.env'
    mock_dotenv.dotenv_values.return_value = {
        'EXISTING_VAR': 'new_value',
        'NEW_VAR': 'new_var_value',
        'NONE_VAR': None
    }
    
    with patch.dict('sys.modules', {'dotenv': mock_dotenv}):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Set an existing env var
                monkeypatch.setenv('EXISTING_VAR', 'original_value')
                
                # Clear other vars
                if 'NEW_VAR' in os.environ:
                    monkeypatch.delenv('NEW_VAR')
                if 'NONE_VAR' in os.environ:
                    monkeypatch.delenv('NONE_VAR')
                
                result = flask.cli.load_dotenv(load_defaults=True)
                assert result is True
                
                # Existing var should not be changed
                assert os.environ['EXISTING_VAR'] == 'original_value'
                # New var should be set
                assert os.environ['NEW_VAR'] == 'new_var_value'
                # None value should be skipped
                assert 'NONE_VAR' not in os.environ
                
            finally:
                os.chdir(original_cwd)
                # Clean up
                if 'NEW_VAR' in os.environ:
                    monkeypatch.delenv('NEW_VAR')

def test_load_dotenv_no_default_files_found(monkeypatch):
    """Test load_dotenv when no default files are found."""
    mock_dotenv = MagicMock()
    mock_dotenv.find_dotenv.return_value = None  # No default files found
    
    with patch.dict('sys.modules', {'dotenv': mock_dotenv}):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Ensure no env files exist
                assert not os.path.isfile('.env')
                assert not os.path.isfile('.flaskenv')
                
                result = flask.cli.load_dotenv(load_defaults=True)
                assert result is False
                mock_dotenv.dotenv_values.assert_not_called()
                
            finally:
                os.chdir(original_cwd)

def test_load_dotenv_empty_data_dict(monkeypatch):
    """Test load_dotenv when data dictionary is empty."""
    mock_dotenv = MagicMock()
    mock_dotenv.find_dotenv.return_value = None
    mock_dotenv.dotenv_values.return_value = {}
    
    with patch.dict('sys.modules', {'dotenv': mock_dotenv}):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_env_file = os.path.join(tmpdir, 'empty.env')
            with open(custom_env_file, 'w') as f:
                f.write('')
            
            result = flask.cli.load_dotenv(path=custom_env_file, load_defaults=False)
            assert result is False
