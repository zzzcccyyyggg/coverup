# file: src/click/src/click/formatting.py:185-187
# asked: {"lines": [185, 187], "branches": []}
# gained: {"lines": [185, 187], "branches": []}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterWriteHeading:
    def test_write_heading_with_current_indent(self):
        """Test that write_heading correctly indents the heading based on current_indent."""
        formatter = HelpFormatter()
        formatter.current_indent = 4
        formatter.write_heading("Test Heading")
        
        expected = f"{'':>4}Test Heading:\n"
        assert formatter.buffer[-1] == expected
    
    def test_write_heading_with_zero_indent(self):
        """Test that write_heading works correctly with zero current_indent."""
        formatter = HelpFormatter()
        formatter.current_indent = 0
        formatter.write_heading("Another Heading")
        
        expected = "Another Heading:\n"
        assert formatter.buffer[-1] == expected
    
    def test_write_heading_multiple_calls(self):
        """Test that write_heading works correctly when called multiple times."""
        formatter = HelpFormatter()
        formatter.current_indent = 2
        
        formatter.write_heading("First Heading")
        formatter.write_heading("Second Heading")
        
        expected_first = f"{'':>2}First Heading:\n"
        expected_second = f"{'':>2}Second Heading:\n"
        
        assert formatter.buffer[-2] == expected_first
        assert formatter.buffer[-1] == expected_second
