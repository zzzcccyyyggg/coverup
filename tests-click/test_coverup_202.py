# file: src/click/src/click/formatting.py:194-208
# asked: {"lines": [194, 198, 199, 200, 201, 202, 203, 204, 205, 208], "branches": []}
# gained: {"lines": [194, 198, 199, 200, 201, 202, 203, 204, 205, 208], "branches": []}

import pytest
from click.formatting import HelpFormatter, wrap_text


class TestHelpFormatterWriteText:
    """Test cases for HelpFormatter.write_text method to achieve full coverage."""
    
    def test_write_text_with_preserve_paragraphs(self):
        """Test write_text with preserve_paragraphs=True (lines 194-208)."""
        formatter = HelpFormatter(width=40)
        formatter.current_indent = 4
        
        # Test text that will trigger the preserve_paragraphs path
        text = "This is a long paragraph that should be wrapped to fit within the specified width when preserve_paragraphs is True."
        
        formatter.write_text(text)
        
        # Verify the buffer contains the wrapped text
        assert len(formatter.buffer) > 0
        # Verify the text ends with a newline
        result = formatter.getvalue()
        assert result.endswith('\n')
    
    def test_write_text_empty_string(self):
        """Test write_text with empty string."""
        formatter = HelpFormatter(width=40)
        formatter.current_indent = 2
        
        formatter.write_text("")
        
        # Should just write a newline
        result = formatter.getvalue()
        assert result == "\n"
    
    def test_write_text_single_line(self):
        """Test write_text with single line that doesn't need wrapping."""
        formatter = HelpFormatter(width=80)
        formatter.current_indent = 0
        
        text = "Short line"
        formatter.write_text(text)
        
        result = formatter.getvalue()
        assert text in result
        assert result.endswith('\n')
    
    def test_write_text_with_indent(self):
        """Test write_text with indentation."""
        formatter = HelpFormatter(width=30)  # Narrow width to force wrapping
        formatter.current_indent = 4
        
        text = "This text should be indented by 4 spaces on each line when wrapped."
        formatter.write_text(text)
        
        result = formatter.getvalue()
        lines = result.strip().split('\n')
        
        # Check that each line starts with 4 spaces (except possibly the first line)
        # The first line might not have the indent if it's short enough
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                if i > 0:  # Subsequent lines should have the indent
                    assert line.startswith('    '), f"Line {i} '{line}' does not start with 4 spaces"
    
    def test_write_text_multiple_paragraphs(self):
        """Test write_text with multiple paragraphs."""
        formatter = HelpFormatter(width=40)
        formatter.current_indent = 2
        
        text = "First paragraph with some content.\n\nSecond paragraph with different content."
        formatter.write_text(text)
        
        result = formatter.getvalue()
        # Should contain both paragraphs separated by empty lines
        assert "First paragraph" in result
        assert "Second paragraph" in result
        assert result.endswith('\n')
    
    def test_write_text_very_long_line(self):
        """Test write_text with a very long line that forces multiple wraps."""
        formatter = HelpFormatter(width=20)
        formatter.current_indent = 2
        
        text = "This is an extremely long line of text that will definitely need to be wrapped multiple times to fit within the very narrow width constraint."
        formatter.write_text(text)
        
        result = formatter.getvalue()
        lines = result.strip().split('\n')
        
        # Should have multiple lines due to wrapping
        assert len(lines) > 1
        # Subsequent lines should start with 2 spaces
        for i, line in enumerate(lines):
            if line.strip() and i > 0:  # Skip first line and empty lines
                assert line.startswith('  '), f"Line {i} '{line}' does not start with 2 spaces"
        assert result.endswith('\n')
    
    def test_write_text_with_paragraph_indent_preservation(self):
        """Test write_text with paragraphs that have different indentation."""
        formatter = HelpFormatter(width=50)
        formatter.current_indent = 0
        
        # Text with multiple paragraphs with different indentation
        text = "First paragraph.\n\n  Second paragraph with 2-space indent.\n\n    Third paragraph with 4-space indent."
        formatter.write_text(text)
        
        result = formatter.getvalue()
        assert "First paragraph" in result
        assert "Second paragraph" in result  
        assert "Third paragraph" in result
        assert result.endswith('\n')
