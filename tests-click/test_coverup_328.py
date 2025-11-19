# file: src/click/src/click/core.py:1793-1795
# asked: {"lines": [1793, 1794, 1795], "branches": []}
# gained: {"lines": [1793, 1794, 1795], "branches": []}

import pytest
from click.core import Group, Context, Command
from click.formatting import HelpFormatter
from unittest.mock import Mock, patch

class TestGroupFormatOptions:
    def test_format_options_calls_super_and_format_commands(self):
        # Create a mock Group instance
        group = Group('test_group')
        
        # Create mock context and formatter
        ctx = Context(group)
        formatter = HelpFormatter()
        
        # Track calls to super().format_options and format_commands
        super_called = False
        format_commands_called = False
        
        def mock_super_format_options(self, ctx, fmt):
            nonlocal super_called
            super_called = True
        
        def mock_format_commands(self, ctx, fmt):
            nonlocal format_commands_called
            format_commands_called = True
        
        # Patch the methods using context managers to avoid cleanup issues
        with patch.object(Command, 'format_options', mock_super_format_options):
            with patch.object(Group, 'format_commands', mock_format_commands):
                # Call the method under test
                group.format_options(ctx, formatter)
        
        # Verify both methods were called
        assert super_called, "super().format_options was not called"
        assert format_commands_called, "format_commands was not called"

    def test_format_options_with_commands_integration(self):
        # Create a Group with subcommands
        group = Group('test_group')
        
        # Add a subcommand
        @group.command()
        def subcommand():
            """A test subcommand"""
            pass
        
        # Create context and formatter
        ctx = Context(group)
        formatter = HelpFormatter()
        
        # Call format_options - this should execute lines 1793-1795
        group.format_options(ctx, formatter)
        
        # Verify the formatter has content from both parent and commands
        # The parent format_options adds options section, format_commands adds commands section
        result = formatter.getvalue()
        assert 'Options:' in result
        assert 'Commands:' in result
        assert 'subcommand' in result
