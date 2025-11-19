# file: src/click/src/click/core.py:2610-2615
# asked: {"lines": [2610, 2614, 2615], "branches": []}
# gained: {"lines": [2610, 2614, 2615], "branches": []}

import pytest
import click
from click.core import Context, Option, Argument


class TestParameterGetErrorHint:
    """Test cases for Parameter.get_error_hint method to achieve full coverage."""
    
    def test_get_error_hint_with_opts(self):
        """Test get_error_hint when opts is not empty (Option case)."""
        # Create an Option with multiple flags
        option = Option(param_decls=['--option', '-o'])
        ctx = Context(click.Command('test'))
        
        result = option.get_error_hint(ctx)
        
        # Should return formatted options
        assert result == "'--option' / '-o'"
    
    def test_get_error_hint_without_opts(self):
        """Test get_error_hint when opts is empty (Argument case)."""
        # Create an Argument which has empty opts
        argument = Argument(param_decls=['argname'])
        ctx = Context(click.Command('test'))
        
        result = argument.get_error_hint(ctx)
        
        # Should return formatted human_readable_name (which is uppercase for arguments)
        assert result == "'ARGNAME'"
