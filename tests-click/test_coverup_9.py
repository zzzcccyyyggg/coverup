# file: src/click/src/click/_textwrap.py:8-51
# asked: {"lines": [8, 9, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 34, 35, 37, 38, 40, 41, 43, 44, 46, 47, 49, 51], "branches": [[18, 19], [18, 24], [24, 0], [24, 25], [43, 44], [43, 51], [46, 47], [46, 49]]}
# gained: {"lines": [8, 9, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 34, 35, 37, 38, 40, 41, 43, 44, 46, 47, 49, 51], "branches": [[18, 19], [18, 24], [24, 0], [24, 25], [43, 44], [43, 51], [46, 47], [46, 49]]}

import pytest
from click._textwrap import TextWrapper

class TestTextWrapper:
    
    def test_handle_long_word_break_long_words(self):
        """Test _handle_long_word when break_long_words is True"""
        wrapper = TextWrapper(width=10, break_long_words=True)
        reversed_chunks = ["verylongword"]
        cur_line = []
        cur_len = 0
        
        wrapper._handle_long_word(reversed_chunks, cur_line, cur_len, 10)
        
        assert cur_line == ["verylongwo"]
        assert reversed_chunks == ["rd"]
    
    def test_handle_long_word_no_break_long_words_empty_line(self):
        """Test _handle_long_word when break_long_words is False and cur_line is empty"""
        wrapper = TextWrapper(width=10, break_long_words=False)
        reversed_chunks = ["word"]
        cur_line = []
        cur_len = 0
        
        wrapper._handle_long_word(reversed_chunks, cur_line, cur_len, 10)
        
        assert cur_line == ["word"]
        assert reversed_chunks == []
    
    def test_handle_long_word_no_break_long_words_non_empty_line(self):
        """Test _handle_long_word when break_long_words is False and cur_line is not empty"""
        wrapper = TextWrapper(width=10, break_long_words=False)
        reversed_chunks = ["word"]
        cur_line = ["some"]
        cur_len = 4
        
        wrapper._handle_long_word(reversed_chunks, cur_line, cur_len, 10)
        
        # Should not modify anything when break_long_words is False and cur_line is not empty
        assert cur_line == ["some"]
        assert reversed_chunks == ["word"]
    
    def test_extra_indent_context_manager(self):
        """Test the extra_indent context manager"""
        wrapper = TextWrapper(initial_indent="> ", subsequent_indent="  ")
        
        initial_before = wrapper.initial_indent
        subsequent_before = wrapper.subsequent_indent
        
        with wrapper.extra_indent("  "):
            assert wrapper.initial_indent == ">   "
            assert wrapper.subsequent_indent == "    "
        
        # Should restore original values
        assert wrapper.initial_indent == initial_before
        assert wrapper.subsequent_indent == subsequent_before
    
    def test_extra_indent_context_manager_exception(self):
        """Test that extra_indent restores state even when exception occurs"""
        wrapper = TextWrapper(initial_indent="> ", subsequent_indent="  ")
        
        initial_before = wrapper.initial_indent
        subsequent_before = wrapper.subsequent_indent
        
        try:
            with wrapper.extra_indent("  "):
                assert wrapper.initial_indent == ">   "
                assert wrapper.subsequent_indent == "    "
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Should restore original values even after exception
        assert wrapper.initial_indent == initial_before
        assert wrapper.subsequent_indent == subsequent_before
    
    def test_indent_only_first_line(self):
        """Test indent_only with first line only"""
        wrapper = TextWrapper(initial_indent="> ", subsequent_indent="  ")
        text = "First line"
        
        result = wrapper.indent_only(text)
        
        assert result == "> First line"
    
    def test_indent_only_multiple_lines(self):
        """Test indent_only with multiple lines"""
        wrapper = TextWrapper(initial_indent="> ", subsequent_indent="  ")
        text = "First line\nSecond line\nThird line"
        
        result = wrapper.indent_only(text)
        
        expected = "> First line\n  Second line\n  Third line"
        assert result == expected
    
    def test_indent_only_empty_string(self):
        """Test indent_only with empty string"""
        wrapper = TextWrapper(initial_indent="> ", subsequent_indent="  ")
        text = ""
        
        result = wrapper.indent_only(text)
        
        assert result == ""
    
    def test_indent_only_single_newline(self):
        """Test indent_only with just a newline"""
        wrapper = TextWrapper(initial_indent="> ", subsequent_indent="  ")
        text = "\n"
        
        result = wrapper.indent_only(text)
        
        # When text is "\n", splitlines() returns [''], so we get one line with initial indent
        assert result == "> "
    
    def test_indent_only_multiple_newlines(self):
        """Test indent_only with multiple newlines"""
        wrapper = TextWrapper(initial_indent="> ", subsequent_indent="  ")
        text = "\n\n"
        
        result = wrapper.indent_only(text)
        
        # splitlines() returns ['', ''], so we get initial indent + two subsequent indents
        assert result == "> \n  "
