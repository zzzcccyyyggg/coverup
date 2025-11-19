# file: src/click/src/click/core.py:561-573
# asked: {"lines": [561, 571, 572], "branches": []}
# gained: {"lines": [561, 571, 572], "branches": []}

import pytest
from click.core import Context
from click.formatting import HelpFormatter

class MockCommand:
    def __init__(self):
        self.allow_extra_args = False
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False

class TestContextMakeFormatter:
    def test_make_formatter_with_terminal_width_and_max_content_width(self):
        """Test that make_formatter creates a HelpFormatter with correct width parameters."""
        command = MockCommand()
        context = Context(
            command=command,
            terminal_width=100,
            max_content_width=90
        )
        
        formatter = context.make_formatter()
        
        assert isinstance(formatter, HelpFormatter)
        assert formatter.width == 100
        # Note: HelpFormatter constructor applies max_width constraint
        # The actual width might be constrained by max_content_width
        
    def test_make_formatter_with_none_widths(self):
        """Test that make_formatter handles None values for width parameters."""
        command = MockCommand()
        context = Context(
            command=command,
            terminal_width=None,
            max_content_width=None
        )
        
        formatter = context.make_formatter()
        
        assert isinstance(formatter, HelpFormatter)
        # When widths are None, HelpFormatter uses its own defaults
        
    def test_make_formatter_with_custom_formatter_class(self):
        """Test that make_formatter uses custom formatter_class when set."""
        class CustomFormatter(HelpFormatter):
            def __init__(self, width=None, max_width=None):
                super().__init__(width=width, max_width=max_width)
                self.custom_attr = "custom"
        
        command = MockCommand()
        context = Context(
            command=command,
            terminal_width=80,
            max_content_width=70
        )
        context.formatter_class = CustomFormatter
        
        formatter = context.make_formatter()
        
        assert isinstance(formatter, CustomFormatter)
        assert formatter.custom_attr == "custom"
        assert formatter.width == 80
