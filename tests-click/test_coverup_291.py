# file: src/click/src/click/globals.py:12-13
# asked: {"lines": [12, 13], "branches": []}
# gained: {"lines": [12, 13], "branches": []}

import pytest
import click
from click.globals import get_current_context, push_context, pop_context
from click.core import Context


def test_get_current_context_with_silent_false():
    """Test that get_current_context with silent=False returns Context when context exists."""
    ctx = Context(click.Command('test'))
    push_context(ctx)
    try:
        result = get_current_context(silent=False)
        assert isinstance(result, Context)
        assert result == ctx
    finally:
        pop_context()


def test_get_current_context_with_silent_false_no_context():
    """Test that get_current_context with silent=False raises RuntimeError when no context exists."""
    # Ensure no context is set
    while get_current_context(silent=True) is not None:
        pop_context()
    
    with pytest.raises(RuntimeError, match="There is no active click context"):
        get_current_context(silent=False)
