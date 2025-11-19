# file: src/flask/src/flask/cli.py:37-38
# asked: {"lines": [37, 38], "branches": []}
# gained: {"lines": [37, 38], "branches": []}

import pytest
import click
from flask.cli import NoAppException


def test_no_app_exception_inheritance():
    """Test that NoAppException properly inherits from click.UsageError."""
    # Test that NoAppException is a subclass of click.UsageError
    assert issubclass(NoAppException, click.UsageError)
    
    # Test that NoAppException can be instantiated
    exception = NoAppException("Test message")
    assert isinstance(exception, click.UsageError)
    assert str(exception) == "Test message"


def test_no_app_exception_docstring():
    """Test that NoAppException has the correct docstring."""
    assert NoAppException.__doc__ == "Raised if an application cannot be found or loaded."
