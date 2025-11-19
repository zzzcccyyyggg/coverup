# file: src/click/src/click/core.py:993-1000
# asked: {"lines": [993, 998, 999, 1000], "branches": []}
# gained: {"lines": [993, 998, 999, 1000], "branches": []}

import pytest
import click
from click.core import Command, Context
from click.formatting import HelpFormatter

class TestCommandGetUsage:
    """Test cases for Command.get_usage method to achieve full coverage."""
    
    def test_get_usage_basic(self):
        """Test basic usage formatting without any parameters."""
        cmd = Command(name="test_command")
        ctx = Context(cmd, info_name="test_command")
        
        usage = cmd.get_usage(ctx)
        
        # Should return a non-empty string
        assert isinstance(usage, str)
        assert len(usage) > 0
        # Should not end with newline (due to rstrip("\n"))
        assert not usage.endswith("\n")
        # Should contain the command name
        assert "test_command" in usage
    
    def test_get_usage_with_formatter_content(self):
        """Test that get_usage properly uses the formatter and returns formatted content."""
        cmd = Command(name="mycmd")
        ctx = Context(cmd, info_name="mycmd")
        
        # Mock the format_usage method to add content to the formatter
        original_format_usage = cmd.format_usage
        
        def mock_format_usage(ctx, formatter):
            formatter.write("Usage: mycmd [OPTIONS]")
        
        cmd.format_usage = mock_format_usage
        
        try:
            usage = cmd.get_usage(ctx)
            
            # Verify the content from our mock was included
            assert "Usage: mycmd [OPTIONS]" in usage
            # Should not end with newline
            assert not usage.endswith("\n")
        finally:
            # Restore original method
            cmd.format_usage = original_format_usage
    
    def test_get_usage_with_newline_removal(self):
        """Test that trailing newlines are properly removed from formatter output."""
        cmd = Command(name="testcmd")
        ctx = Context(cmd, info_name="testcmd")
        
        # Mock format_usage to add content with trailing newline
        original_format_usage = cmd.format_usage
        
        def mock_format_usage(ctx, formatter):
            formatter.write("Usage: testcmd\n")
        
        cmd.format_usage = mock_format_usage
        
        try:
            usage = cmd.get_usage(ctx)
            
            # Should have the content but without trailing newline
            assert usage == "Usage: testcmd"
            assert not usage.endswith("\n")
        finally:
            cmd.format_usage = original_format_usage
    
    def test_get_usage_multiple_newlines(self):
        """Test that only trailing newlines are removed, not internal ones."""
        cmd = Command(name="multiline")
        ctx = Context(cmd, info_name="multiline")
        
        # Mock format_usage to add content with multiple newlines
        original_format_usage = cmd.format_usage
        
        def mock_format_usage(ctx, formatter):
            formatter.write("Line 1\nLine 2\nLine 3\n")
        
        cmd.format_usage = mock_format_usage
        
        try:
            usage = cmd.get_usage(ctx)
            
            # Should preserve internal newlines but remove trailing one
            assert usage == "Line 1\nLine 2\nLine 3"
            assert usage.count("\n") == 2
            assert not usage.endswith("\n")
        finally:
            cmd.format_usage = original_format_usage
    
    def test_get_usage_empty_formatter(self):
        """Test behavior when formatter returns empty content."""
        cmd = Command(name="empty")
        ctx = Context(cmd, info_name="empty")
        
        # Mock format_usage to not write anything
        original_format_usage = cmd.format_usage
        
        def mock_format_usage(ctx, formatter):
            pass  # Don't write anything
        
        cmd.format_usage = mock_format_usage
        
        try:
            usage = cmd.get_usage(ctx)
            
            # Should return empty string when nothing is written
            assert usage == ""
        finally:
            cmd.format_usage = original_format_usage
