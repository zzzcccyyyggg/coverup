# file: src/flask/src/flask/cli.py:440-446
# asked: {"lines": [440, 441, 442, 444, 445, 446], "branches": [[441, 442], [441, 444]]}
# gained: {"lines": [440, 441, 442, 444, 445, 446], "branches": [[441, 442], [441, 444]]}

import pytest
import click
from flask.cli import ScriptInfo, _set_app

def test_set_app_with_value():
    """Test _set_app when a value is provided."""
    ctx = click.Context(click.Command('test'))
    ctx.obj = ScriptInfo()
    
    # Call _set_app with a value
    result = _set_app(ctx, None, 'myapp')
    
    # Verify the value is returned
    assert result == 'myapp'
    # Verify the app_import_path is set on the ScriptInfo object
    assert ctx.obj.app_import_path == 'myapp'

def test_set_app_with_none():
    """Test _set_app when None is provided."""
    ctx = click.Context(click.Command('test'))
    ctx.obj = ScriptInfo()
    
    # Call _set_app with None
    result = _set_app(ctx, None, None)
    
    # Verify None is returned and app_import_path remains unchanged
    assert result is None
    assert ctx.obj.app_import_path is None
