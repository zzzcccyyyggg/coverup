# file: src/click/src/click/termui.py:647-656
# asked: {"lines": [647, 656], "branches": []}
# gained: {"lines": [647, 656], "branches": []}

import pytest
from click.termui import unstyle


class TestUnstyle:
    def test_unstyle_with_ansi_codes(self):
        """Test that unstyle removes ANSI escape sequences from text."""
        text_with_ansi = "\033[31mRed Text\033[0m"
        result = unstyle(text_with_ansi)
        assert result == "Red Text"
    
    def test_unstyle_without_ansi_codes(self):
        """Test that unstyle returns plain text unchanged."""
        plain_text = "Plain text without ANSI codes"
        result = unstyle(plain_text)
        assert result == plain_text
    
    def test_unstyle_with_multiple_ansi_codes(self):
        """Test that unstyle removes multiple ANSI escape sequences."""
        text_with_multiple_ansi = "\033[1mBold\033[0m and \033[3mItalic\033[0m"
        result = unstyle(text_with_multiple_ansi)
        assert result == "Bold and Italic"
    
    def test_unstyle_with_empty_string(self):
        """Test that unstyle handles empty strings correctly."""
        result = unstyle("")
        assert result == ""
    
    def test_unstyle_with_only_ansi_codes(self):
        """Test that unstyle handles strings containing only ANSI codes."""
        only_ansi = "\033[31m\033[0m"
        result = unstyle(only_ansi)
        assert result == ""
