# file: src/click/src/click/formatting.py:278-280
# asked: {"lines": [278, 280], "branches": []}
# gained: {"lines": [278, 280], "branches": []}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterGetValue:
    def test_getvalue_empty_buffer(self):
        """Test getvalue returns empty string when buffer is empty."""
        formatter = HelpFormatter()
        result = formatter.getvalue()
        assert result == ""
    
    def test_getvalue_with_content(self):
        """Test getvalue returns joined buffer content."""
        formatter = HelpFormatter()
        formatter.buffer = ["Hello", " ", "World", "!"]
        result = formatter.getvalue()
        assert result == "Hello World!"
