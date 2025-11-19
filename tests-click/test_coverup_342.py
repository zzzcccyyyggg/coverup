# file: src/click/src/click/core.py:1954-1958
# asked: {"lines": [1954, 1955], "branches": []}
# gained: {"lines": [1954, 1955], "branches": []}

import pytest
import click
from click.core import _MultiCommand, _FakeSubclassCheck


def test_multicommand_deprecation_message():
    """Test that _MultiCommand has correct deprecation message in docstring."""
    assert ".. deprecated:: 8.2" in _MultiCommand.__doc__
    assert "Will be removed in Click 9.0" in _MultiCommand.__doc__
    assert "Use ``Group`` instead" in _MultiCommand.__doc__


def test_multicommand_inheritance():
    """Test that _MultiCommand inherits from Group and uses _FakeSubclassCheck metaclass."""
    assert issubclass(_MultiCommand, click.Group)
    assert type(_MultiCommand) == _FakeSubclassCheck


def test_multicommand_instantiation():
    """Test that _MultiCommand can be instantiated without errors."""
    # This test ensures lines 1954-1955 are executed during class definition
    cmd = _MultiCommand()
    assert isinstance(cmd, click.Group)
    assert isinstance(cmd, _MultiCommand)
