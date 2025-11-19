# file: src/click/src/click/_compat.py:488-489
# asked: {"lines": [488, 489], "branches": []}
# gained: {"lines": [488, 489], "branches": []}

import pytest
import re
from click._compat import strip_ansi, _ansi_re

class TestStripAnsi:
    def test_strip_ansi_with_ansi_codes(self):
        """Test that ANSI escape sequences are properly stripped from strings."""
        # Test various ANSI escape sequences
        test_cases = [
            ("\033[31mHello\033[0m", "Hello"),
            ("\033[1;32mBold Green\033[0m", "Bold Green"),
            ("\033[38;5;208mOrange\033[0m", "Orange"),
            ("\033[48;5;226mYellow Background\033[0m", "Yellow Background"),
            ("\033[?25lCursor Hidden\033[?25h", "Cursor Hidden"),
            ("\033[2JClear Screen", "Clear Screen"),
            ("\033[HHome", "Home"),
            ("\033[0mReset", "Reset"),
            ("\033[1mBold\033[22mNormal", "BoldNormal"),
            ("\033[3mItalic\033[23mNormal", "ItalicNormal"),
        ]
        
        for input_str, expected in test_cases:
            result = strip_ansi(input_str)
            assert result == expected, f"Failed for input: {repr(input_str)}"
    
    def test_strip_ansi_without_ansi_codes(self):
        """Test that strings without ANSI codes remain unchanged."""
        test_cases = [
            "Hello World",
            "Plain text",
            "No escape sequences here",
            "",
            "12345",
            "Special chars: !@#$%^&*()",
        ]
        
        for input_str in test_cases:
            result = strip_ansi(input_str)
            assert result == input_str, f"Failed for input: {repr(input_str)}"
    
    def test_strip_ansi_mixed_content(self):
        """Test strings with mixed ANSI codes and regular text."""
        test_cases = [
            ("Normal \033[31mRed\033[0m Normal", "Normal Red Normal"),
            ("Start\033[1mBold\033[22mEnd", "StartBoldEnd"),
            ("\033[32mGreen\033[0m and \033[34mBlue\033[0m", "Green and Blue"),
        ]
        
        for input_str, expected in test_cases:
            result = strip_ansi(input_str)
            assert result == expected, f"Failed for input: {repr(input_str)}"
    
    def test_strip_ansi_multiple_sequences(self):
        """Test strings with multiple consecutive ANSI sequences."""
        test_cases = [
            ("\033[31m\033[1mBold Red\033[0m", "Bold Red"),
            ("\033[32m\033[3mItalic Green\033[23m\033[0m", "Italic Green"),
            ("\033[1m\033[4mBold Underline\033[24m\033[22m", "Bold Underline"),
        ]
        
        for input_str, expected in test_cases:
            result = strip_ansi(input_str)
            assert result == expected, f"Failed for input: {repr(input_str)}"
