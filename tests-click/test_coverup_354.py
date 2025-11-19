# file: src/click/src/click/core.py:2607-2608
# asked: {"lines": [2607, 2608], "branches": []}
# gained: {"lines": [2607, 2608], "branches": []}

import pytest
import click
from click.core import Context, Option, Argument

class TestParameterGetUsagePieces:
    def test_option_get_usage_pieces_returns_empty_list(self):
        """Test that Option.get_usage_pieces returns an empty list."""
        ctx = Context(click.Command('test'))
        option = Option(['--test-option'])
        result = option.get_usage_pieces(ctx)
        assert result == []

    def test_argument_get_usage_pieces_returns_metavar(self):
        """Test that Argument.get_usage_pieces returns the metavar."""
        ctx = Context(click.Command('test'))
        argument = Argument(['test_arg'])
        result = argument.get_usage_pieces(ctx)
        assert result == ['TEST_ARG']
