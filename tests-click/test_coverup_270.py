# file: src/click/src/click/core.py:1088-1095
# asked: {"lines": [1088, 1093, 1094, 1095], "branches": []}
# gained: {"lines": [1088, 1093, 1094, 1095], "branches": []}

import pytest
from click.core import Command, Context
from click.formatting import HelpFormatter

class TestCommandGetHelp:
    def test_get_help_returns_formatted_help(self):
        """Test that get_help returns formatted help string without trailing newline."""
        # Create a mock command that implements format_help
        class TestCommand(Command):
            def format_help(self, ctx, formatter):
                formatter.write("Test help content")
        
        command = TestCommand(name="test")
        ctx = Context(command=command)
        
        # Call get_help and verify the result
        result = command.get_help(ctx)
        
        # Verify the result is the formatted help without trailing newline
        assert result == "Test help content"
        
    def test_get_help_with_trailing_newline_removed(self):
        """Test that get_help removes trailing newline from formatter output."""
        # Create a mock command that adds trailing newline in format_help
        class TestCommand(Command):
            def format_help(self, ctx, formatter):
                formatter.write("Test help content\n")
        
        command = TestCommand(name="test")
        ctx = Context(command=command)
        
        # Call get_help and verify trailing newline is removed
        result = command.get_help(ctx)
        
        # Verify the result has no trailing newline
        assert result == "Test help content"
        
    def test_get_help_with_multiple_trailing_newlines_removed(self):
        """Test that get_help removes multiple trailing newlines from formatter output."""
        # Create a mock command that adds multiple trailing newlines
        class TestCommand(Command):
            def format_help(self, ctx, formatter):
                formatter.write("Test help content\n\n\n")
        
        command = TestCommand(name="test")
        ctx = Context(command=command)
        
        # Call get_help and verify all trailing newlines are removed
        result = command.get_help(ctx)
        
        # Verify the result has no trailing newlines
        assert result == "Test help content"
        
    def test_get_help_calls_format_help(self, monkeypatch):
        """Test that get_help properly calls format_help method."""
        # Track if format_help was called
        format_help_called = False
        
        class TestCommand(Command):
            def format_help(self, ctx, formatter):
                nonlocal format_help_called
                format_help_called = True
                formatter.write("Test help")
        
        command = TestCommand(name="test")
        ctx = Context(command=command)
        
        # Call get_help
        result = command.get_help(ctx)
        
        # Verify format_help was called
        assert format_help_called is True
        assert result == "Test help"
        
    def test_get_help_uses_context_formatter(self, monkeypatch):
        """Test that get_help uses the formatter created by the context."""
        # Track formatter creation and usage
        formatter_created = False
        original_make_formatter = Context.make_formatter
        
        def mock_make_formatter(self):
            nonlocal formatter_created
            formatter_created = True
            return original_make_formatter(self)
        
        class TestCommand(Command):
            def format_help(self, ctx, formatter):
                formatter.write("Test help")
        
        command = TestCommand(name="test")
        ctx = Context(command=command)
        
        # Monkeypatch make_formatter to track calls
        monkeypatch.setattr(Context, "make_formatter", mock_make_formatter)
        
        # Call get_help
        result = command.get_help(ctx)
        
        # Verify formatter was created and used
        assert formatter_created is True
        assert result == "Test help"
