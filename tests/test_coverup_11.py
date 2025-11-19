# file: src/flask/src/flask/cli.py:563-598
# asked: {"lines": [563, 565, 566, 567, 568, 569, 572, 577, 579, 580, 582, 583, 585, 587, 589, 590, 591, 593, 594, 595, 596, 598], "branches": [[579, 580], [579, 582], [582, 583], [582, 585], [593, 594], [593, 598]]}
# gained: {"lines": [563, 565, 566, 567, 568, 569, 572, 577, 579, 580, 582, 583, 585, 587, 589, 590, 591, 593, 594, 595, 596, 598], "branches": [[579, 580], [579, 582], [582, 583], [582, 585], [593, 594], [593, 598]]}

import pytest
import click
from flask.cli import FlaskGroup
from unittest.mock import Mock, patch

def test_flaskgroup_init_without_default_commands():
    """Test FlaskGroup initialization without default commands."""
    group = FlaskGroup(add_default_commands=False)
    assert group.create_app is None
    assert group.load_dotenv is True
    assert group.set_debug_flag is True
    assert group._loaded_plugin_commands is False
    # Verify default commands are not added
    assert 'run' not in group.commands
    assert 'shell' not in group.commands
    assert 'routes' not in group.commands

def test_flaskgroup_init_without_version_option():
    """Test FlaskGroup initialization without version option."""
    group = FlaskGroup(add_version_option=False)
    assert group.create_app is None
    assert group.load_dotenv is True
    assert group.set_debug_flag is True
    assert group._loaded_plugin_commands is False
    # Verify version option is not in params
    version_params = [p for p in group.params if hasattr(p, 'name') and p.name == 'version']
    assert len(version_params) == 0

def test_flaskgroup_init_with_custom_context_settings():
    """Test FlaskGroup initialization with custom context settings."""
    custom_settings = {'auto_envvar_prefix': 'CUSTOM'}
    group = FlaskGroup(context_settings=custom_settings)
    assert group.context_settings['auto_envvar_prefix'] == 'CUSTOM'
    assert group.create_app is None
    assert group.load_dotenv is True
    assert group.set_debug_flag is True
    assert group._loaded_plugin_commands is False

def test_flaskgroup_init_with_custom_params():
    """Test FlaskGroup initialization with custom params."""
    custom_param = click.Option(['--custom'], help='Custom option')
    group = FlaskGroup(params=[custom_param])
    assert custom_param in group.params
    assert group.create_app is None
    assert group.load_dotenv is True
    assert group.set_debug_flag is True
    assert group._loaded_plugin_commands is False

def test_flaskgroup_init_with_create_app():
    """Test FlaskGroup initialization with create_app callback."""
    def mock_create_app():
        return Mock()
    
    group = FlaskGroup(create_app=mock_create_app)
    assert group.create_app == mock_create_app
    assert group.load_dotenv is True
    assert group.set_debug_flag is True
    assert group._loaded_plugin_commands is False

def test_flaskgroup_init_without_dotenv():
    """Test FlaskGroup initialization without dotenv loading."""
    group = FlaskGroup(load_dotenv=False)
    assert group.create_app is None
    assert group.load_dotenv is False
    assert group.set_debug_flag is True
    assert group._loaded_plugin_commands is False

def test_flaskgroup_init_without_debug_flag():
    """Test FlaskGroup initialization without debug flag setting."""
    group = FlaskGroup(set_debug_flag=False)
    assert group.create_app is None
    assert group.load_dotenv is True
    assert group.set_debug_flag is False
    assert group._loaded_plugin_commands is False

def test_flaskgroup_init_with_all_options_disabled():
    """Test FlaskGroup initialization with all optional features disabled."""
    group = FlaskGroup(
        add_default_commands=False,
        add_version_option=False,
        load_dotenv=False,
        set_debug_flag=False
    )
    assert group.create_app is None
    assert group.load_dotenv is False
    assert group.set_debug_flag is False
    assert group._loaded_plugin_commands is False
    # Verify no default commands
    assert 'run' not in group.commands
    assert 'shell' not in group.commands
    assert 'routes' not in group.commands
    # Verify no version option
    version_params = [p for p in group.params if hasattr(p, 'name') and p.name == 'version']
    assert len(version_params) == 0

def test_flaskgroup_init_with_extra_kwargs():
    """Test FlaskGroup initialization with extra keyword arguments."""
    group = FlaskGroup(help='Custom help text', name='custom-group')
    assert group.help == 'Custom help text'
    assert group.name == 'custom-group'
    assert group.create_app is None
    assert group.load_dotenv is True
    assert group.set_debug_flag is True
    assert group._loaded_plugin_commands is False
