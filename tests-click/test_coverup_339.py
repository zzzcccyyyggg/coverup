# file: src/click/src/click/formatting.py:139-141
# asked: {"lines": [139, 141], "branches": []}
# gained: {"lines": [139, 141], "branches": []}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterIndent:
    def test_indent_increases_current_indent_by_increment(self):
        formatter = HelpFormatter(indent_increment=2)
        initial_indent = formatter.current_indent
        
        formatter.indent()
        
        assert formatter.current_indent == initial_indent + 2
    
    def test_indent_with_custom_increment(self):
        formatter = HelpFormatter(indent_increment=4)
        initial_indent = formatter.current_indent
        
        formatter.indent()
        
        assert formatter.current_indent == initial_indent + 4
    
    def test_indent_multiple_times(self):
        formatter = HelpFormatter(indent_increment=2)
        initial_indent = formatter.current_indent
        
        formatter.indent()
        formatter.indent()
        formatter.indent()
        
        assert formatter.current_indent == initial_indent + 6
