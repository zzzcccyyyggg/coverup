# file: src/click/src/click/formatting.py:135-137
# asked: {"lines": [135, 137], "branches": []}
# gained: {"lines": [135, 137], "branches": []}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterWrite:
    def test_write_appends_string_to_buffer(self):
        """Test that write method appends string to internal buffer."""
        formatter = HelpFormatter()
        test_string = "test string"
        
        formatter.write(test_string)
        
        assert formatter.buffer == [test_string]
    
    def test_write_multiple_strings(self):
        """Test that multiple write calls append multiple strings to buffer."""
        formatter = HelpFormatter()
        strings = ["first", "second", "third"]
        
        for string in strings:
            formatter.write(string)
        
        assert formatter.buffer == strings
    
    def test_write_empty_string(self):
        """Test that write handles empty strings correctly."""
        formatter = HelpFormatter()
        
        formatter.write("")
        
        assert formatter.buffer == [""]
