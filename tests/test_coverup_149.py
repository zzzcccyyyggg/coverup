# file: src/flask/src/flask/cli.py:657-676
# asked: {"lines": [657, 661, 667, 669, 670, 671, 672, 673, 676], "branches": [[669, 670], [669, 676]]}
# gained: {"lines": [657, 661, 667, 669, 670, 671, 672, 673, 676], "branches": [[669, 670], [669, 676]]}

import os
import pytest
import click
from flask.cli import FlaskGroup, ScriptInfo


def test_flaskgroup_make_context_sets_env_var(monkeypatch):
    """Test that make_context sets FLASK_RUN_FROM_CLI environment variable."""
    # Mock the environment to track changes
    env_vars = {}
    monkeypatch.setattr(os, 'environ', env_vars)
    
    # Create a FlaskGroup instance with no_args_is_help=False to avoid parse_args issues
    group = FlaskGroup(no_args_is_help=False)
    
    # Call make_context - this should set the environment variable
    # Use a command that won't trigger help exit
    try:
        context = group.make_context("test", ["routes"])
    except click.exceptions.Exit:
        # If it still exits, try with a subcommand that exists
        context = group.make_context("test", ["--version"])
    
    # Verify the environment variable was set
    assert env_vars.get("FLASK_RUN_FROM_CLI") == "true"
    assert isinstance(context, click.Context)


def test_flaskgroup_make_context_creates_scriptinfo_when_not_provided():
    """Test that make_context creates ScriptInfo when obj is not in extra or context_settings."""
    # Create a FlaskGroup instance with no_args_is_help=False
    group = FlaskGroup(no_args_is_help=False)
    
    # Call make_context without providing 'obj' in extra
    # Use a command that won't trigger help exit
    try:
        context = group.make_context("test", ["routes"])
    except click.exceptions.Exit:
        # If it still exits, try with a subcommand that exists
        context = group.make_context("test", ["--version"])
    
    # Verify that obj was created and is a ScriptInfo instance
    assert hasattr(context, 'obj')
    assert isinstance(context.obj, ScriptInfo)
    assert context.obj.create_app == group.create_app
    assert context.obj.set_debug_flag == group.set_debug_flag
    assert context.obj.load_dotenv_defaults == group.load_dotenv


def test_flaskgroup_make_context_preserves_existing_obj():
    """Test that make_context preserves existing obj when provided in extra."""
    # Create a FlaskGroup instance with no_args_is_help=False
    group = FlaskGroup(no_args_is_help=False)
    
    # Create a ScriptInfo object to pass in (not a dict, to avoid AttributeError)
    custom_obj = ScriptInfo()
    
    # Call make_context with 'obj' in extra
    # Use a command that won't trigger help exit
    try:
        context = group.make_context("test", ["routes"], obj=custom_obj)
    except click.exceptions.Exit:
        # If it still exits, try with a subcommand that exists
        context = group.make_context("test", ["--version"], obj=custom_obj)
    
    # Verify that the custom object was preserved
    assert context.obj == custom_obj


def test_flaskgroup_make_context_preserves_obj_from_context_settings():
    """Test that make_context preserves obj when set in context_settings."""
    # Create a ScriptInfo object for context_settings
    settings_obj = ScriptInfo()
    
    # Create a FlaskGroup instance with obj in context_settings and no_args_is_help=False
    group = FlaskGroup(context_settings={"obj": settings_obj}, no_args_is_help=False)
    
    # Call make_context without providing 'obj' in extra
    # Use a command that won't trigger help exit
    try:
        context = group.make_context("test", ["routes"])
    except click.exceptions.Exit:
        # If it still exits, try with a subcommand that exists
        context = group.make_context("test", ["--version"])
    
    # Verify that the obj from context_settings was preserved
    assert context.obj == settings_obj


def test_flaskgroup_make_context_with_parent_context():
    """Test that make_context works correctly with a parent context."""
    # Create a FlaskGroup instance with no_args_is_help=False
    group = FlaskGroup(no_args_is_help=False)
    
    # Create a parent context
    parent = click.Context(click.Command("parent"))
    
    # Call make_context with parent
    # Use a command that won't trigger help exit
    try:
        context = group.make_context("test", ["routes"], parent=parent)
    except click.exceptions.Exit:
        # If it still exits, try with a subcommand that exists
        context = group.make_context("test", ["--version"], parent=parent)
    
    # Verify the context was created with the correct parent
    assert context.parent == parent
    assert isinstance(context, click.Context)
