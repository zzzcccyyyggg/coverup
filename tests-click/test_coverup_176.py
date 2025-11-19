# file: src/click/src/click/formatting.py:254-267
# asked: {"lines": [254, 255, 261, 262, 263, 264, 265, 267], "branches": []}
# gained: {"lines": [254, 255, 261, 262, 263, 264, 265, 267], "branches": []}

import pytest
from click.formatting import HelpFormatter

class TestHelpFormatterSection:
    def test_section_context_manager(self):
        """Test that section context manager calls all expected methods in correct order."""
        formatter = HelpFormatter()
        
        # Track method calls
        call_order = []
        
        # Mock the methods to track calls
        original_write_paragraph = formatter.write_paragraph
        original_write_heading = formatter.write_heading
        original_indent = formatter.indent
        original_dedent = formatter.dedent
        
        def mock_write_paragraph():
            call_order.append("write_paragraph")
            original_write_paragraph()
        
        def mock_write_heading(name):
            call_order.append(f"write_heading({name})")
            original_write_heading(name)
        
        def mock_indent():
            call_order.append("indent")
            original_indent()
        
        def mock_dedent():
            call_order.append("dedent")
            original_dedent()
        
        formatter.write_paragraph = mock_write_paragraph
        formatter.write_heading = mock_write_heading
        formatter.indent = mock_indent
        formatter.dedent = mock_dedent
        
        # Use the section context manager
        with formatter.section("Test Section"):
            call_order.append("inside context")
        
        # Verify the call order
        expected_order = [
            "write_paragraph",
            "write_heading(Test Section)",
            "indent",
            "inside context",
            "dedent"
        ]
        assert call_order == expected_order
        
        # Verify indentation was properly managed
        assert formatter.current_indent == 0

    def test_section_with_exception(self):
        """Test that section context manager properly dedents even when exception occurs."""
        formatter = HelpFormatter()
        
        # Track method calls
        call_order = []
        
        # Mock the methods to track calls
        original_write_paragraph = formatter.write_paragraph
        original_write_heading = formatter.write_heading
        original_indent = formatter.indent
        original_dedent = formatter.dedent
        
        def mock_write_paragraph():
            call_order.append("write_paragraph")
            original_write_paragraph()
        
        def mock_write_heading(name):
            call_order.append(f"write_heading({name})")
            original_write_heading(name)
        
        def mock_indent():
            call_order.append("indent")
            original_indent()
        
        def mock_dedent():
            call_order.append("dedent")
            original_dedent()
        
        formatter.write_paragraph = mock_write_paragraph
        formatter.write_heading = mock_write_heading
        formatter.indent = mock_indent
        formatter.dedent = mock_dedent
        
        # Use the section context manager with an exception
        try:
            with formatter.section("Test Section"):
                call_order.append("inside context")
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Verify the call order (dedent should still be called)
        expected_order = [
            "write_paragraph",
            "write_heading(Test Section)",
            "indent",
            "inside context",
            "dedent"
        ]
        assert call_order == expected_order
        
        # Verify indentation was properly reset even with exception
        assert formatter.current_indent == 0
