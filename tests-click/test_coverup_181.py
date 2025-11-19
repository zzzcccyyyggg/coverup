# file: src/click/src/click/core.py:1318-1326
# asked: {"lines": [1318, 1319, 1321, 1322, 1323, 1324, 1326], "branches": []}
# gained: {"lines": [1318, 1319, 1321, 1322, 1323, 1324], "branches": []}

import pytest
import click
import typing as t
from click.testing import CliRunner

def test_command_main_overload_true():
    """Test the Command.main overload with standalone_mode=True."""
    
    @click.command()
    def test_cmd():
        click.echo("test")
    
    runner = CliRunner()
    
    # This should trigger the overload with standalone_mode=True
    with pytest.raises(SystemExit):
        test_cmd.main(['--help'], standalone_mode=True)
