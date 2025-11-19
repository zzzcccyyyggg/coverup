# file: src/click/src/click/shell_completion.py:537-559
# asked: {"lines": [537, 543, 544, 546, 547, 549, 551, 552, 553, 555, 556, 557, 559], "branches": [[543, 544], [543, 546], [546, 547], [546, 549], [551, 552], [551, 559], [552, 553], [552, 555], [555, 551], [555, 556]]}
# gained: {"lines": [537, 543, 544, 546, 547, 549, 551, 552, 553, 555, 556, 557, 559], "branches": [[543, 544], [543, 546], [546, 547], [546, 549], [551, 552], [551, 559], [552, 553], [552, 555], [555, 551], [555, 556]]}

import pytest
from click.core import Context, Option, Argument, Command
from click.shell_completion import _is_incomplete_option, _start_of_option


class TestIsIncompleteOption:
    """Test cases for _is_incomplete_option function."""

    def test_non_option_parameter_returns_false(self):
        """Test that non-Option parameters return False."""
        command = Command("test")
        ctx = Context(command)
        param = Argument(["arg"])
        args = ["--option", "value"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_flag_option_returns_false(self):
        """Test that flag options return False."""
        command = Command("test")
        ctx = Context(command)
        param = Option(["--flag"], is_flag=True)
        args = ["--flag"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_count_option_returns_false(self):
        """Test that count options return False."""
        command = Command("test")
        ctx = Context(command)
        param = Option(["--count"], count=True)
        args = ["--count"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_option_with_value_and_matching_last_option_returns_true(self):
        """Test that options requiring values return True when last option matches."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--file"], nargs=1)
        args = ["--file"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is True

    def test_option_with_value_and_non_matching_last_option_returns_false(self):
        """Test that options requiring values return False when last option doesn't match."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--file"], nargs=1)
        args = ["--other"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_option_with_value_and_no_last_option_returns_false(self):
        """Test that options requiring values return False when no option found."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--file"], nargs=1)
        args = ["argument"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_option_with_multiple_nargs_and_matching_last_option(self):
        """Test option with nargs > 1 and matching last option."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--files"], nargs=2)
        args = ["--files", "file1", "--files"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is True

    def test_option_with_multiple_nargs_and_non_matching_last_option(self):
        """Test option with nargs > 1 and non-matching last option."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--files"], nargs=2)
        args = ["--files", "file1", "--other"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_option_with_short_option_match(self):
        """Test with short option that matches."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["-f", "--file"], nargs=1)
        args = ["-f"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is True

    def test_option_with_short_option_no_match(self):
        """Test with short option that doesn't match."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["-f", "--file"], nargs=1)
        args = ["-x"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_option_with_multiple_opts_and_matching_last_option(self):
        """Test option with multiple opts where last option matches one of them."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["-f", "--file", "--filename"], nargs=1)
        args = ["--filename"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is True

    def test_reversed_args_search_behavior(self):
        """Test that the function searches args in reverse order."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--file"], nargs=1)
        args = ["--other", "--file", "value1", "--file"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is True

    def test_nargs_limit_in_reverse_search(self):
        """Test that nargs limits how far back the reverse search goes."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--file"], nargs=1)
        # With nargs=1, only the last arg should be checked
        args = ["--file", "value1", "--file", "value2", "--other"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_empty_args_list_returns_false(self):
        """Test that empty args list returns False."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--file"], nargs=1)
        args = []
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_option_with_nargs_zero_returns_false(self):
        """Test that options with nargs=0 return False."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--file"], nargs=0)
        args = ["--file"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is False

    def test_option_with_multiple_nargs_and_partial_values(self):
        """Test option with nargs > 1 and partial values provided."""
        command = Command("test")
        ctx = Context(command)
        ctx._opt_prefixes = {"-", "--"}
        param = Option(["--files"], nargs=3)
        args = ["--files", "file1", "file2"]
        
        result = _is_incomplete_option(ctx, args, param)
        assert result is True
