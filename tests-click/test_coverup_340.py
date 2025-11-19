# file: src/click/src/click/formatting.py:143-145
# asked: {"lines": [143, 145], "branches": []}
# gained: {"lines": [143, 145], "branches": []}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterDedent:
    def test_dedent_decreases_current_indent_by_indent_increment(self):
        formatter = HelpFormatter(indent_increment=2)
        formatter.current_indent = 4
        
        formatter.dedent()
        
        assert formatter.current_indent == 2

    def test_dedent_multiple_times(self):
        formatter = HelpFormatter(indent_increment=3)
        formatter.current_indent = 9
        
        formatter.dedent()
        formatter.dedent()
        
        assert formatter.current_indent == 3

    def test_dedent_from_zero_indent(self):
        formatter = HelpFormatter(indent_increment=2)
        formatter.current_indent = 0
        
        formatter.dedent()
        
        assert formatter.current_indent == -2
