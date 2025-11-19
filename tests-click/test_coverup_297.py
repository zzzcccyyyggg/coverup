# file: src/click/src/click/_compat.py:568-569
# asked: {"lines": [568, 569], "branches": []}
# gained: {"lines": [568, 569], "branches": []}

import pytest
from click._compat import term_len, strip_ansi

class TestTermLen:
    def test_term_len_with_ansi_codes(self):
        """Test term_len function with ANSI escape codes."""
        # ANSI escape sequence for red text
        text_with_ansi = "\033[31mHello\033[0m World"
        expected_length = len("Hello World")
        result = term_len(text_with_ansi)
        assert result == expected_length

    def test_term_len_without_ansi_codes(self):
        """Test term_len function without ANSI escape codes."""
        text_without_ansi = "Hello World"
        expected_length = len(text_without_ansi)
        result = term_len(text_without_ansi)
        assert result == expected_length

    def test_term_len_empty_string(self):
        """Test term_len function with empty string."""
        result = term_len("")
        assert result == 0

    def test_term_len_only_ansi_codes(self):
        """Test term_len function with only ANSI escape codes."""
        text_only_ansi = "\033[31m\033[0m"
        result = term_len(text_only_ansi)
        assert result == 0
