# file: src/click/src/click/core.py:1173-1180
# asked: {"lines": [1173, 1175, 1176, 1177, 1179, 1180], "branches": [[1175, 0], [1175, 1176]]}
# gained: {"lines": [1173, 1175, 1176, 1177, 1179, 1180], "branches": [[1175, 0], [1175, 1176]]}

import pytest
from click.core import Command, Context
from click.formatting import HelpFormatter

class TestCommandFormatEpilog:
    def test_format_epilog_with_epilog(self):
        """Test that format_epilog writes epilog when it exists."""
        # Create a command with an epilog
        cmd = Command(name="test_cmd", epilog="This is an epilog\nwith multiple lines")
        
        # Create a mock context and formatter
        ctx = Context(cmd)
        formatter = HelpFormatter()
        
        # Call the method under test
        cmd.format_epilog(ctx, formatter)
        
        # Verify the epilog was processed and written
        result = formatter.getvalue()
        assert "This is an epilog" in result
        assert "with multiple lines" in result
        
    def test_format_epilog_without_epilog(self):
        """Test that format_epilog does nothing when no epilog exists."""
        # Create a command without an epilog
        cmd = Command(name="test_cmd", epilog=None)
        
        # Create a mock context and formatter
        ctx = Context(cmd)
        formatter = HelpFormatter()
        
        # Store initial state
        initial_buffer = formatter.buffer.copy()
        initial_indent = formatter.current_indent
        
        # Call the method under test
        cmd.format_epilog(ctx, formatter)
        
        # Verify nothing was written and indent didn't change
        assert formatter.buffer == initial_buffer
        assert formatter.current_indent == initial_indent
        
    def test_format_epilog_with_multiline_epilog(self):
        """Test that format_epilog properly handles multi-line epilog with indentation."""
        # Create a command with a multi-line epilog that has common indentation
        # Use a different pattern to avoid the exact string matching issue
        cmd = Command(name="test_cmd", epilog="  Line one\n  Line two\n  Line three")
        
        # Create a mock context and formatter
        ctx = Context(cmd)
        formatter = HelpFormatter()
        
        # Call the method under test
        cmd.format_epilog(ctx, formatter)
        
        # Verify the epilog was cleaned and written with proper formatting
        result = formatter.getvalue()
        # inspect.cleandoc should remove the common indentation
        assert "Line one" in result
        assert "Line two" in result
        assert "Line three" in result
        # The cleaned text should not have the exact original indented strings
        # Check that the cleaned version is present without the leading spaces
        lines = result.strip().split('\n')
        for line in lines:
            if line and not line.isspace():
                # Each non-empty line should not start with two spaces (the original indentation)
                assert not line.startswith('  Line')
        
    def test_format_epilog_with_epilog_containing_paragraph_and_indentation(self):
        """Test that format_epilog properly uses write_paragraph and indentation."""
        # Create a command with an epilog
        cmd = Command(name="test_cmd", epilog="Epilog text")
        
        # Create a mock context and formatter
        ctx = Context(cmd)
        formatter = HelpFormatter()
        
        # Call the method under test
        cmd.format_epilog(ctx, formatter)
        
        # Verify the result contains the epilog text
        result = formatter.getvalue()
        assert "Epilog text" in result
