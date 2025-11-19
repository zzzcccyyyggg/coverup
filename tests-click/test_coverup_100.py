# file: src/click/src/click/parser.py:111-117
# asked: {"lines": [111, 112, 113, 114, 115, 116, 117], "branches": [[113, 114], [113, 115], [115, 116], [115, 117]]}
# gained: {"lines": [111, 112, 113, 114, 115, 116, 117], "branches": [[113, 114], [113, 115], [115, 116], [115, 117]]}

import pytest
from click.parser import _split_opt

class TestSplitOpt:
    def test_split_opt_alnum_first_character(self):
        """Test when first character is alphanumeric - returns empty string and full opt"""
        result = _split_opt("abc")
        assert result == ("", "abc")
    
    def test_split_opt_double_prefix(self):
        """Test when option has double prefix (e.g., --)"""
        result = _split_opt("--option")
        assert result == ("--", "option")
    
    def test_split_opt_single_prefix(self):
        """Test when option has single prefix (e.g., -)"""
        result = _split_opt("-o")
        assert result == ("-", "o")
    
    def test_split_opt_special_char_prefix(self):
        """Test when option has special character prefix"""
        result = _split_opt("+flag")
        assert result == ("+", "flag")
    
    def test_split_opt_empty_string(self):
        """Test with empty string"""
        result = _split_opt("")
        assert result == ("", "")
