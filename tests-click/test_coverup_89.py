# file: src/click/src/click/shell_completion.py:466-500
# asked: {"lines": [466, 484, 486, 487, 488, 489, 491, 492, 493, 494, 498, 500], "branches": [[492, 493], [492, 500]]}
# gained: {"lines": [466, 484, 486, 487, 488, 489, 491, 492, 493, 494, 498, 500], "branches": [[492, 493], [492, 500]]}

import pytest
from click.shell_completion import split_arg_string

class TestSplitArgString:
    """Test cases for split_arg_string function to achieve full coverage."""
    
    def test_split_arg_string_normal_case(self):
        """Test normal case where no ValueError is raised."""
        result = split_arg_string("example normal string")
        assert result == ["example", "normal", "string"]
    
    def test_split_arg_string_with_quotes(self):
        """Test case with properly closed quotes."""
        result = split_arg_string('example "quoted string"')
        assert result == ["example", "quoted string"]
    
    def test_split_arg_string_incomplete_quote(self):
        """Test case with incomplete quote that triggers ValueError."""
        result = split_arg_string("example 'incomplete quote")
        assert result == ["example", "incomplete quote"]
    
    def test_split_arg_string_incomplete_escape(self):
        """Test case with incomplete escape sequence that triggers ValueError."""
        result = split_arg_string("example incomplete\\")
        assert result == ["example", "incomplete"]
    
    def test_split_arg_string_empty_string(self):
        """Test case with empty string."""
        result = split_arg_string("")
        assert result == []
    
    def test_split_arg_string_only_whitespace(self):
        """Test case with only whitespace."""
        result = split_arg_string("   ")
        assert result == []
    
    def test_split_arg_string_multiple_incomplete_tokens(self):
        """Test case with multiple incomplete tokens."""
        # The backslash at the end should be preserved in the token
        result = split_arg_string("first 'incomplete second\\")
        assert result == ["first", "incomplete second\\"]
