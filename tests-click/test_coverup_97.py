# file: src/click/src/click/core.py:1907-1932
# asked: {"lines": [1907, 1910, 1911, 1914, 1918, 1919, 1920, 1928, 1929, 1930, 1931, 1932], "branches": [[1918, 1919], [1918, 1928], [1928, 1929], [1928, 1932], [1929, 1930], [1929, 1931]]}
# gained: {"lines": [1907, 1910, 1911, 1914, 1918, 1919, 1920, 1928, 1929, 1930, 1931, 1932], "branches": [[1918, 1919], [1918, 1928], [1928, 1929], [1928, 1932], [1929, 1930], [1929, 1931]]}

import pytest
from click.core import Group, Context
from click.parser import _split_opt
from click.utils import make_str
from gettext import gettext as _

class MockCommand:
    def __init__(self, name):
        self.name = name

class TestGroupResolveCommand:
    def test_resolve_command_with_token_normalize_func(self, monkeypatch):
        """Test that token_normalize_func is used when command is not found initially."""
        group = Group()
        mock_command = MockCommand("normalized_cmd")
        
        def mock_get_command(ctx, cmd_name):
            if cmd_name == "normalized_cmd":
                return mock_command
            return None
        
        group.get_command = mock_get_command
        
        ctx = Context(group)
        ctx.resilient_parsing = True  # Prevent fail() from raising
        ctx.token_normalize_func = lambda x: "normalized_cmd" if x == "cmd" else x
        
        args = ["cmd"]
        result = group.resolve_command(ctx, args)
        
        assert result == ("normalized_cmd", mock_command, [])

    def test_resolve_command_with_option_like_cmd_and_resilient_parsing_false(self, monkeypatch):
        """Test that parse_args is called when command looks like an option and resilient_parsing is False."""
        group = Group()
        
        def mock_get_command(ctx, cmd_name):
            return None
        
        group.get_command = mock_get_command
        
        parse_args_called = []
        def mock_parse_args(ctx, args):
            parse_args_called.append((ctx, args))
            return []  # parse_args returns remaining args
        
        group.parse_args = mock_parse_args
        
        fail_called = []
        def mock_fail(message):
            fail_called.append(message)
            # Don't raise to allow test to continue
        
        ctx = Context(group)
        ctx.resilient_parsing = False
        ctx.fail = mock_fail
        
        args = ["--help"]
        result = group.resolve_command(ctx, args)
        
        assert result == (None, None, [])
        assert len(parse_args_called) == 1
        assert parse_args_called[0] == (ctx, args)
        assert len(fail_called) == 1
        assert "No such command '--help'." in fail_called[0]

    def test_resolve_command_with_non_option_like_cmd_and_resilient_parsing_false(self, monkeypatch):
        """Test that parse_args is NOT called when command doesn't look like an option and resilient_parsing is False."""
        group = Group()
        
        def mock_get_command(ctx, cmd_name):
            return None
        
        group.get_command = mock_get_command
        
        parse_args_called = []
        def mock_parse_args(ctx, args):
            parse_args_called.append((ctx, args))
            return []
        
        group.parse_args = mock_parse_args
        
        fail_called = []
        def mock_fail(message):
            fail_called.append(message)
        
        ctx = Context(group)
        ctx.resilient_parsing = False
        ctx.fail = mock_fail
        
        args = ["nonexistent"]
        result = group.resolve_command(ctx, args)
        
        assert result == (None, None, [])
        assert len(parse_args_called) == 0
        assert len(fail_called) == 1
        assert "No such command 'nonexistent'." in fail_called[0]

    def test_resolve_command_with_resilient_parsing_true(self, monkeypatch):
        """Test that when resilient_parsing is True, no fail is called and parse_args is not called."""
        group = Group()
        
        def mock_get_command(ctx, cmd_name):
            return None
        
        group.get_command = mock_get_command
        
        parse_args_called = []
        def mock_parse_args(ctx, args):
            parse_args_called.append((ctx, args))
            return []
        
        group.parse_args = mock_parse_args
        
        fail_called = []
        def mock_fail(message):
            fail_called.append(message)
        
        ctx = Context(group)
        ctx.resilient_parsing = True
        ctx.fail = mock_fail
        
        args = ["--help"]
        result = group.resolve_command(ctx, args)
        
        assert result == (None, None, [])
        assert len(parse_args_called) == 0
        assert len(fail_called) == 0

    def test_resolve_command_successful_find(self):
        """Test successful command resolution without normalization."""
        group = Group()
        mock_command = MockCommand("test_cmd")
        
        def mock_get_command(ctx, cmd_name):
            if cmd_name == "test_cmd":
                return mock_command
            return None
        
        group.get_command = mock_get_command
        
        ctx = Context(group)
        ctx.resilient_parsing = True  # Prevent fail() from raising
        
        args = ["test_cmd", "arg1", "arg2"]
        result = group.resolve_command(ctx, args)
        
        assert result == ("test_cmd", mock_command, ["arg1", "arg2"])

    def test_resolve_command_with_token_normalize_func_no_match(self, monkeypatch):
        """Test that token_normalize_func is used but still no command found."""
        group = Group()
        
        def mock_get_command(ctx, cmd_name):
            return None
        
        group.get_command = mock_get_command
        
        fail_called = []
        def mock_fail(message):
            fail_called.append(message)
        
        ctx = Context(group)
        ctx.resilient_parsing = False
        ctx.token_normalize_func = lambda x: x.upper()
        ctx.fail = mock_fail
        
        args = ["cmd"]
        result = group.resolve_command(ctx, args)
        
        assert result == (None, None, [])
        assert len(fail_called) == 1
        assert "No such command 'cmd'." in fail_called[0]
