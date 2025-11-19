# file: src/click/src/click/shell_completion.py:623-667
# asked: {"lines": [623, 638, 639, 640, 641, 642, 648, 649, 651, 655, 656, 657, 661, 662, 663, 667], "branches": [[638, 639], [638, 640], [640, 641], [640, 648], [648, 649], [648, 651], [655, 656], [655, 661], [656, 655], [656, 657], [661, 662], [661, 667], [662, 661], [662, 663]]}
# gained: {"lines": [623, 638, 639, 640, 641, 642, 648, 649, 651, 655, 656, 657, 661, 662, 663, 667], "branches": [[638, 639], [638, 640], [640, 641], [640, 648], [648, 649], [648, 651], [655, 656], [655, 661], [656, 655], [656, 657], [661, 662], [661, 667], [662, 661], [662, 663]]}

import pytest
from click.core import Command, Context, Parameter, Option, Argument
from click.shell_completion import _resolve_incomplete, _start_of_option, _is_incomplete_option, _is_incomplete_argument


class TestResolveIncomplete:
    def test_resolve_incomplete_with_equals_sign(self, monkeypatch):
        """Test when incomplete is '=' (line 638-639)"""
        ctx = Context(Command("test"))
        args = []
        incomplete = "="
        
        result_obj, result_incomplete = _resolve_incomplete(ctx, args, incomplete)
        
        assert result_obj == ctx.command
        assert result_incomplete == ""
        assert args == []

    def test_resolve_incomplete_with_option_equals_value(self, monkeypatch):
        """Test when incomplete contains '=' and starts with option (line 640-642)"""
        ctx = Context(Command("test"))
        monkeypatch.setattr(ctx, "_opt_prefixes", {"-", "--"})
        args = []
        incomplete = "--option=value"
        
        result_obj, result_incomplete = _resolve_incomplete(ctx, args, incomplete)
        
        assert result_obj == ctx.command
        assert result_incomplete == "value"
        assert args == ["--option"]

    def test_resolve_incomplete_option_name_completion(self, monkeypatch):
        """Test when incomplete starts with option and no '--' marker (line 648-649)"""
        ctx = Context(Command("test"))
        monkeypatch.setattr(ctx, "_opt_prefixes", {"-", "--"})
        args = []
        incomplete = "--opt"
        
        result_obj, result_incomplete = _resolve_incomplete(ctx, args, incomplete)
        
        assert result_obj == ctx.command
        assert result_incomplete == "--opt"

    def test_resolve_incomplete_with_double_dash_marker(self, monkeypatch):
        """Test when '--' marker is present in args (line 648)"""
        ctx = Context(Command("test"))
        monkeypatch.setattr(ctx, "_opt_prefixes", {"-", "--"})
        args = ["--"]
        incomplete = "--should-not-complete"
        
        result_obj, result_incomplete = _resolve_incomplete(ctx, args, incomplete)
        
        # Should not return at line 649, continue to check params
        assert result_obj == ctx.command
        assert result_incomplete == "--should-not-complete"

    def test_resolve_incomplete_option_value_completion(self, monkeypatch):
        """Test when last arg is an option that needs a value (line 655-657)"""
        ctx = Context(Command("test"))
        monkeypatch.setattr(ctx, "_opt_prefixes", {"-", "--"})
        
        # Create an option that needs a value
        opt = Option(["--file"], type=str)
        cmd = ctx.command
        monkeypatch.setattr(cmd, "get_params", lambda ctx: [opt])
        
        # Mock _is_incomplete_option to return True for our option
        def mock_is_incomplete_option(ctx, args, param):
            return param is opt
        
        monkeypatch.setattr("click.shell_completion._is_incomplete_option", mock_is_incomplete_option)
        
        args = ["--file"]
        incomplete = "some_value"
        
        result_obj, result_incomplete = _resolve_incomplete(ctx, args, incomplete)
        
        assert result_obj == opt
        assert result_incomplete == "some_value"

    def test_resolve_incomplete_argument_completion(self, monkeypatch):
        """Test when there's an incomplete argument (line 661-663)"""
        ctx = Context(Command("test"))
        monkeypatch.setattr(ctx, "_opt_prefixes", {"-", "--"})
        
        # Create an argument with a list containing the name
        arg = Argument(["filename"])
        cmd = ctx.command
        monkeypatch.setattr(cmd, "get_params", lambda ctx: [arg])
        
        # Mock _is_incomplete_argument to return True for our argument
        def mock_is_incomplete_argument(ctx, param):
            return param is arg
        
        monkeypatch.setattr("click.shell_completion._is_incomplete_argument", mock_is_incomplete_argument)
        
        args = []
        incomplete = "file"
        
        result_obj, result_incomplete = _resolve_incomplete(ctx, args, incomplete)
        
        assert result_obj == arg
        assert result_incomplete == "file"

    def test_resolve_incomplete_fallback_to_command(self, monkeypatch):
        """Test fallback to command when no params match (line 667)"""
        ctx = Context(Command("test"))
        monkeypatch.setattr(ctx, "_opt_prefixes", {"-", "--"})
        
        # Create params that won't match
        opt = Option(["--flag"], is_flag=True)
        cmd = ctx.command
        monkeypatch.setattr(cmd, "get_params", lambda ctx: [opt])
        
        # Mock both _is_incomplete_option and _is_incomplete_argument to return False
        monkeypatch.setattr("click.shell_completion._is_incomplete_option", lambda ctx, args, param: False)
        monkeypatch.setattr("click.shell_completion._is_incomplete_argument", lambda ctx, param: False)
        
        args = []
        incomplete = "something"
        
        result_obj, result_incomplete = _resolve_incomplete(ctx, args, incomplete)
        
        assert result_obj == ctx.command
        assert result_incomplete == "something"
