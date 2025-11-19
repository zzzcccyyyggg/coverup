# file: src/click/src/click/shell_completion.py:528-534
# asked: {"lines": [528, 530, 531, 533, 534], "branches": [[530, 531], [530, 533]]}
# gained: {"lines": [528, 530, 531, 533, 534], "branches": [[530, 531], [530, 533]]}

import pytest
from click.core import Context
from click import Command
from click.shell_completion import _start_of_option


class TestStartOfOption:
    """Test cases for _start_of_option function."""

    def test_start_of_option_empty_string(self):
        """Test that empty string returns False."""
        ctx = Context(Command("test"))
        result = _start_of_option(ctx, "")
        assert result is False

    def test_start_of_option_with_opt_prefix(self):
        """Test that string starting with option prefix returns True."""
        ctx = Context(Command("test"))
        ctx._opt_prefixes = {"-", "--"}
        
        # Test with single dash
        result = _start_of_option(ctx, "-option")
        assert result is True
        
        # Test with double dash
        result = _start_of_option(ctx, "--option")
        assert result is True

    def test_start_of_option_without_opt_prefix(self):
        """Test that string not starting with option prefix returns False."""
        ctx = Context(Command("test"))
        ctx._opt_prefixes = {"-", "--"}
        
        # Test with regular string
        result = _start_of_option(ctx, "option")
        assert result is False
        
        # Test with different character
        result = _start_of_option(ctx, "+option")
        assert result is False

    def test_start_of_option_custom_prefixes(self):
        """Test with custom option prefixes."""
        ctx = Context(Command("test"))
        ctx._opt_prefixes = {"+", "++"}
        
        # Test with custom prefix
        result = _start_of_option(ctx, "+option")
        assert result is True
        
        # Test with custom double prefix
        result = _start_of_option(ctx, "++option")
        assert result is True
        
        # Test that standard dash doesn't work
        result = _start_of_option(ctx, "-option")
        assert result is False

    def test_start_of_option_single_character(self):
        """Test with single character strings."""
        ctx = Context(Command("test"))
        ctx._opt_prefixes = {"-", "--"}
        
        # Test single dash
        result = _start_of_option(ctx, "-")
        assert result is True
        
        # Test single non-option character
        result = _start_of_option(ctx, "a")
        assert result is False
