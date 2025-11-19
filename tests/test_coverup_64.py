# file: src/flask/src/flask/cli.py:305-331
# asked: {"lines": [305, 307, 308, 309, 310, 313, 316, 319, 320, 322, 323, 331], "branches": []}
# gained: {"lines": [305, 307, 308, 309, 310, 313, 316, 319, 320, 322, 323, 331], "branches": []}

import pytest
from flask.cli import ScriptInfo
from flask.app import Flask

def test_scriptinfo_init_defaults():
    """Test ScriptInfo initialization with default parameters."""
    info = ScriptInfo()
    assert info.app_import_path is None
    assert info.create_app is None
    assert info.data == {}
    assert info.set_debug_flag is True
    assert info.load_dotenv_defaults is True
    assert info._loaded_app is None

def test_scriptinfo_init_custom_params():
    """Test ScriptInfo initialization with custom parameters."""
    
    def dummy_create_app():
        return Flask(__name__)
    
    info = ScriptInfo(
        app_import_path="myapp:app",
        create_app=dummy_create_app,
        set_debug_flag=False,
        load_dotenv_defaults=False
    )
    
    assert info.app_import_path == "myapp:app"
    assert info.create_app == dummy_create_app
    assert info.data == {}
    assert info.set_debug_flag is False
    assert info.load_dotenv_defaults is False
    assert info._loaded_app is None

def test_scriptinfo_init_load_dotenv_none():
    """Test ScriptInfo initialization with load_dotenv_defaults=None."""
    info = ScriptInfo(load_dotenv_defaults=None)
    assert info.load_dotenv_defaults is None

def test_scriptinfo_init_load_dotenv_false():
    """Test ScriptInfo initialization with load_dotenv_defaults=False."""
    info = ScriptInfo(load_dotenv_defaults=False)
    assert info.load_dotenv_defaults is False

def test_scriptinfo_init_empty_data_dict():
    """Test that ScriptInfo.data is initialized as an empty dictionary."""
    info = ScriptInfo()
    assert isinstance(info.data, dict)
    assert len(info.data) == 0
    # Test that we can modify the data dictionary
    info.data["test_key"] = "test_value"
    assert info.data["test_key"] == "test_value"
