# file: src/click/src/click/core.py:1137-1159
# asked: {"lines": [1137, 1139, 1141, 1143, 1145, 1146, 1147, 1148, 1149, 1151, 1152, 1155, 1156, 1158, 1159], "branches": [[1139, 1141], [1139, 1143], [1145, 1146], [1145, 1155], [1155, 0], [1155, 1156]]}
# gained: {"lines": [1137, 1139, 1141, 1143, 1145, 1146, 1147, 1148, 1149, 1151, 1152, 1155, 1156, 1158, 1159], "branches": [[1139, 1141], [1139, 1143], [1145, 1146], [1145, 1155], [1155, 0], [1155, 1156]]}

import pytest
from click.core import Command, Context
from click.formatting import HelpFormatter


class TestCommandFormatHelpText:
    """Test cases for Command.format_help_text method to achieve full coverage."""
    
    def test_format_help_text_with_help_and_deprecated_string(self):
        """Test format_help_text with help text and deprecated string message."""
        command = Command(name="test_cmd", help="Test help text", deprecated="Use new_cmd instead")
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        assert "Test help text" in result
        assert "(DEPRECATED: Use new_cmd instead)" in result
    
    def test_format_help_text_with_help_and_deprecated_bool(self):
        """Test format_help_text with help text and deprecated=True."""
        command = Command(name="test_cmd", help="Test help text", deprecated=True)
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        assert "Test help text" in result
        assert "(DEPRECATED)" in result
    
    def test_format_help_text_with_help_and_form_feed(self):
        """Test format_help_text with help text containing form feed character."""
        command = Command(name="test_cmd", help="First part\fSecond part")
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        assert "First part" in result
        assert "Second part" not in result
    
    def test_format_help_text_with_help_only(self):
        """Test format_help_text with help text only (no deprecated)."""
        command = Command(name="test_cmd", help="Simple help text")
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        assert "Simple help text" in result
        assert "(DEPRECATED)" not in result
    
    def test_format_help_text_without_help(self):
        """Test format_help_text when help is None."""
        command = Command(name="test_cmd", help=None)
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        # Should not write anything when help is None
        assert result == ""
    
    def test_format_help_text_with_empty_help(self):
        """Test format_help_text when help is empty string."""
        command = Command(name="test_cmd", help="")
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        # Should not write anything when help is empty
        assert result == ""
    
    def test_format_help_text_with_deprecated_only(self):
        """Test format_help_text when only deprecated is set (no help text)."""
        command = Command(name="test_cmd", help=None, deprecated=True)
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        # Should write only the deprecated message
        assert "(DEPRECATED)" in result
    
    def test_format_help_text_with_deprecated_string_only(self):
        """Test format_help_text when only deprecated string is set (no help text)."""
        command = Command(name="test_cmd", help=None, deprecated="Use new command")
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        # Should write only the deprecated message with custom text
        assert "(DEPRECATED: Use new command)" in result
    
    def test_format_help_text_with_cleaned_docstring(self):
        """Test format_help_text with help text that needs cleaning (inspect.cleandoc)."""
        command = Command(name="test_cmd", help="    Help text with\n    leading spaces")
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        command.format_help_text(ctx, formatter)
        result = formatter.getvalue()
        
        # inspect.cleandoc should remove common leading whitespace
        assert "Help text with" in result
        assert "leading spaces" in result
        # Should not have the leading spaces from the original string
        assert "    Help text with" not in result
