# file: src/flask/src/flask/cli.py:267-280
# asked: {"lines": [267, 268, 269, 271, 272, 274, 275, 276, 277, 278, 280], "branches": [[268, 269], [268, 271]]}
# gained: {"lines": [267, 268, 269, 271, 272, 274, 275, 276, 277, 278, 280], "branches": [[268, 269], [268, 271]]}

import pytest
import click
from unittest.mock import patch, MagicMock
import importlib.metadata
import platform


def test_get_version_with_value_and_not_resilient_parsing():
    """Test get_version function when value is True and resilient_parsing is False."""
    mock_ctx = MagicMock(spec=click.Context)
    mock_ctx.resilient_parsing = False
    mock_ctx.color = True
    
    with patch('importlib.metadata.version') as mock_version, \
         patch('click.echo') as mock_echo, \
         patch('platform.python_version', return_value='3.10.0'):
        
        mock_version.side_effect = lambda pkg: {
            'flask': '2.3.0',
            'werkzeug': '2.3.0'
        }[pkg]
        
        from flask.cli import get_version
        
        get_version(mock_ctx, None, True)
        
        mock_echo.assert_called_once_with(
            "Python 3.10.0\nFlask 2.3.0\nWerkzeug 2.3.0",
            color=True
        )
        mock_ctx.exit.assert_called_once()


def test_get_version_with_value_and_resilient_parsing():
    """Test get_version function when value is True but resilient_parsing is True."""
    mock_ctx = MagicMock(spec=click.Context)
    mock_ctx.resilient_parsing = True
    
    from flask.cli import get_version
    
    get_version(mock_ctx, None, True)
    
    mock_ctx.exit.assert_not_called()


def test_get_version_with_false_value():
    """Test get_version function when value is False."""
    mock_ctx = MagicMock(spec=click.Context)
    mock_ctx.resilient_parsing = False
    
    from flask.cli import get_version
    
    get_version(mock_ctx, None, False)
    
    mock_ctx.exit.assert_not_called()
