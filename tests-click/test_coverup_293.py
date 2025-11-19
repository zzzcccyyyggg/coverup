# file: src/click/src/click/exceptions.py:259-265
# asked: {"lines": [259, 260], "branches": []}
# gained: {"lines": [259, 260], "branches": []}

import pytest
import click
from click.exceptions import BadArgumentUsage


def test_bad_argument_usage_instantiation():
    """Test that BadArgumentUsage can be instantiated with a message."""
    message = "Argument usage error occurred"
    exception = BadArgumentUsage(message)
    
    assert isinstance(exception, BadArgumentUsage)
    assert isinstance(exception, click.exceptions.UsageError)
    assert str(exception) == message
    assert exception.ctx is None
    assert exception.cmd is None


def test_bad_argument_usage_with_context():
    """Test that BadArgumentUsage can be instantiated with a context."""
    ctx = click.Context(click.Command('test_command'))
    message = "Argument usage error with context"
    exception = BadArgumentUsage(message, ctx)
    
    assert isinstance(exception, BadArgumentUsage)
    assert isinstance(exception, click.exceptions.UsageError)
    assert str(exception) == message
    assert exception.ctx is ctx
    assert exception.cmd is ctx.command


def test_bad_argument_usage_inheritance():
    """Test that BadArgumentUsage properly inherits from UsageError."""
    exception = BadArgumentUsage("test")
    
    # Check inheritance chain
    assert isinstance(exception, BadArgumentUsage)
    assert isinstance(exception, click.exceptions.UsageError)
    assert isinstance(exception, click.exceptions.ClickException)
    assert isinstance(exception, Exception)
    
    # Check that it has the expected exit code from UsageError
    assert exception.exit_code == 2
