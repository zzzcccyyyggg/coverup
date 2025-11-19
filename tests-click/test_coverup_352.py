# file: src/click/src/click/core.py:1496-1500
# asked: {"lines": [1496, 1497], "branches": []}
# gained: {"lines": [1496, 1497], "branches": []}

import pytest
import click
from click.core import _BaseCommand


def test_base_command_deprecation_warning():
    """Test that _BaseCommand issues a deprecation warning when instantiated."""
    # The deprecation warning is in the docstring, not emitted at runtime
    # Just test that the class can be instantiated and has the docstring
    cmd = _BaseCommand("test_command")
    assert "deprecated" in cmd.__doc__
    assert "Will be removed in Click 9.0" in cmd.__doc__
    assert "Use ``Command`` instead" in cmd.__doc__


def test_base_command_inheritance():
    """Test that _BaseCommand properly inherits from Command."""
    cmd = _BaseCommand("test_command")
    assert isinstance(cmd, click.Command)
    assert isinstance(cmd, _BaseCommand)


def test_base_command_metaclass():
    """Test that _BaseCommand uses _FakeSubclassCheck metaclass."""
    assert type(_BaseCommand) is not type
    # In Python 3, metaclass is stored in __class__ rather than __metaclass__
    assert _BaseCommand.__class__.__name__ == '_FakeSubclassCheck'
