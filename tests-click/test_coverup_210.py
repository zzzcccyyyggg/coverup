# file: src/click/src/click/formatting.py:269-276
# asked: {"lines": [269, 270, 272, 273, 274, 276], "branches": []}
# gained: {"lines": [269, 270, 272, 273, 274, 276], "branches": []}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterIndentation:
    def test_indentation_context_manager_increases_and_decreases_indent(self):
        """Test that the indentation context manager properly increases and decreases indentation."""
        formatter = HelpFormatter(indent_increment=2)
        
        # Initial state
        assert formatter.current_indent == 0
        
        # Use the context manager
        with formatter.indentation():
            # Inside context - indentation should be increased
            assert formatter.current_indent == 2
        
        # After context - indentation should be restored
        assert formatter.current_indent == 0

    def test_indentation_context_manager_with_exception_still_dedents(self):
        """Test that the indentation context manager properly dedents even when an exception occurs."""
        formatter = HelpFormatter(indent_increment=2)
        
        # Initial state
        assert formatter.current_indent == 0
        
        try:
            with formatter.indentation():
                # Inside context - indentation should be increased
                assert formatter.current_indent == 2
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # After context (even with exception) - indentation should be restored
        assert formatter.current_indent == 0
