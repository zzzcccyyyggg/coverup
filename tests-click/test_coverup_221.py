# file: src/click/src/click/formatting.py:189-192
# asked: {"lines": [189, 191, 192], "branches": [[191, 0], [191, 192]]}
# gained: {"lines": [189, 191, 192], "branches": [[191, 0], [191, 192]]}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterWriteParagraph:
    def test_write_paragraph_with_buffer(self):
        """Test write_paragraph when buffer has content"""
        formatter = HelpFormatter()
        formatter.buffer = ["existing content"]
        formatter.write_paragraph()
        assert formatter.buffer == ["existing content", "\n"]
    
    def test_write_paragraph_without_buffer(self):
        """Test write_paragraph when buffer is empty"""
        formatter = HelpFormatter()
        formatter.buffer = []
        formatter.write_paragraph()
        assert formatter.buffer == []
