# file: src/click/src/click/core.py:2885-2889
# asked: {"lines": [2885, 2886, 2887, 2888, 2889], "branches": [[2887, 2888], [2887, 2889]]}
# gained: {"lines": [2885, 2886, 2887, 2888, 2889], "branches": [[2887, 2888], [2887, 2889]]}

import pytest
import click
from click.core import Context, Option


class TestOptionGetErrorHint:
    """Test cases for Option.get_error_hint method to achieve full coverage."""
    
    def test_get_error_hint_without_envvar(self):
        """Test get_error_hint when show_envvar is False or envvar is None."""
        # Case 1: show_envvar is False
        option = Option(['--test'], show_envvar=False, envvar='TEST_VAR')
        ctx = Context(click.Command('test_cmd'))
        result = option.get_error_hint(ctx)
        assert result == "'--test'"
        
        # Case 2: envvar is None
        option = Option(['--test'], show_envvar=True, envvar=None)
        result = option.get_error_hint(ctx)
        assert result == "'--test'"
    
    def test_get_error_hint_with_envvar(self):
        """Test get_error_hint when show_envvar is True and envvar is set."""
        option = Option(['--test'], show_envvar=True, envvar='TEST_VAR')
        ctx = Context(click.Command('test_cmd'))
        result = option.get_error_hint(ctx)
        assert result == "'--test' (env var: 'TEST_VAR')"
    
    def test_get_error_hint_multiple_opts_with_envvar(self):
        """Test get_error_hint with multiple options and envvar."""
        option = Option(['-t', '--test'], show_envvar=True, envvar='TEST_VAR')
        ctx = Context(click.Command('test_cmd'))
        result = option.get_error_hint(ctx)
        assert result == "'-t' / '--test' (env var: 'TEST_VAR')"
