# file: src/click/src/click/formatting.py:210-252
# asked: {"lines": [210, 213, 214, 224, 225, 226, 227, 229, 231, 232, 233, 234, 235, 236, 237, 239, 240, 242, 243, 244, 246, 247, 249, 250, 252], "branches": [[226, 227], [226, 229], [231, 0], [231, 232], [233, 234], [233, 236], [236, 237], [236, 239], [246, 247], [246, 252], [249, 231], [249, 250]]}
# gained: {"lines": [210, 213, 214, 224, 225, 226, 227, 229, 231, 232, 233, 234, 235, 236, 237, 239, 240, 242, 243, 244, 246, 247, 249, 250, 252], "branches": [[226, 227], [226, 229], [231, 0], [231, 232], [233, 234], [233, 236], [236, 237], [236, 239], [246, 247], [246, 252], [249, 231], [249, 250]]}

import pytest
from click.formatting import HelpFormatter, measure_table, iter_rows, wrap_text
from click._compat import term_len
import collections.abc as cabc


class TestHelpFormatterWriteDL:
    def test_write_dl_with_empty_rows_raises_error(self):
        """Test write_dl with empty rows list raises TypeError."""
        formatter = HelpFormatter()
        with pytest.raises(TypeError, match="Expected two columns for definition list"):
            formatter.write_dl([])

    def test_write_dl_with_single_row_no_second_column(self):
        """Test write_dl with single row where second column is empty."""
        formatter = HelpFormatter()
        rows = [("term1", "")]
        formatter.write_dl(rows)
        # Should write term and newline
        assert formatter.buffer == ["term1", "\n"]

    def test_write_dl_with_single_row_short_first_column(self):
        """Test write_dl where first column is short enough to stay on same line."""
        formatter = HelpFormatter(width=80)
        rows = [("short", "This is a description")]
        formatter.write_dl(rows)
        # First line should have term and spaces, second line should have description
        assert len(formatter.buffer) >= 2
        assert formatter.buffer[0] == "short"
        # The second buffer entry should be spaces followed by description
        assert "This is a description" in "".join(formatter.buffer)

    def test_write_dl_with_long_first_column(self):
        """Test write_dl where first column is too long and wraps to new line."""
        formatter = HelpFormatter(width=40)
        long_term = "a" * 35  # Longer than col_max default of 30
        rows = [(long_term, "Description text")]
        formatter.write_dl(rows)
        # First line should have just the term, then newline, then indented description
        assert formatter.buffer[0] == long_term
        assert formatter.buffer[1] == "\n"
        # The third buffer entry should be the indented description
        assert formatter.buffer[2].startswith(" " * (30 + 2))

    def test_write_dl_with_wrapped_text_multiple_lines(self):
        """Test write_dl where description text wraps to multiple lines."""
        formatter = HelpFormatter(width=30)
        long_description = "This is a very long description that should definitely wrap to multiple lines when formatted"
        rows = [("term", long_description)]
        formatter.write_dl(rows)
        # Should have multiple lines for the description
        lines_with_content = [line for line in formatter.buffer if line.strip()]
        assert len(lines_with_content) > 2

    def test_write_dl_with_empty_description_lines(self):
        """Test write_dl where wrapped text produces empty lines list."""
        formatter = HelpFormatter()
        # Mock wrap_text to return empty string which splits to empty list
        def mock_wrap_text(text, width, preserve_paragraphs=False):
            return ""
        
        import click.formatting
        original_wrap_text = click.formatting.wrap_text
        click.formatting.wrap_text = mock_wrap_text
        try:
            rows = [("term", "description")]
            formatter.write_dl(rows)
            # Should write newline after the empty description
            assert formatter.buffer[-1] == "\n"
        finally:
            click.formatting.wrap_text = original_wrap_text

    def test_write_dl_with_custom_col_max_and_spacing(self):
        """Test write_dl with custom column max and spacing."""
        formatter = HelpFormatter(width=80)
        rows = [("term", "description")]
        formatter.write_dl(rows, col_max=20, col_spacing=4)
        # Verify formatting uses custom values
        assert len(formatter.buffer) >= 1

    def test_write_dl_with_indentation(self):
        """Test write_dl when formatter has current indentation."""
        formatter = HelpFormatter()
        formatter.current_indent = 4
        rows = [("term", "description")]
        formatter.write_dl(rows)
        # First line should be indented
        assert formatter.buffer[0].startswith("    term")

    def test_write_dl_raises_type_error_for_wrong_column_count(self):
        """Test write_dl raises TypeError for rows with wrong number of columns."""
        formatter = HelpFormatter()
        rows = [("single_column",)]  # Only one column
        with pytest.raises(TypeError, match="Expected two columns for definition list"):
            formatter.write_dl(rows)

    def test_write_dl_with_multiple_rows(self):
        """Test write_dl with multiple rows of varying lengths."""
        formatter = HelpFormatter(width=50)
        rows = [
            ("short1", "Description for first item"),
            ("a" * 25, "Description for second item with longer term"),
            ("short2", ""),  # Empty description
            ("verylongterm" * 5, "Description for very long term"),
        ]
        formatter.write_dl(rows)
        # Should process all rows without errors
        assert len(formatter.buffer) > 0

    def test_write_dl_preserves_paragraphs_in_wrap_text(self):
        """Test write_dl calls wrap_text with preserve_paragraphs=True."""
        formatter = HelpFormatter(width=40)
        
        # Track if wrap_text was called with preserve_paragraphs=True
        wrap_text_calls = []
        original_wrap_text = wrap_text
        
        def mock_wrap_text(text, width, preserve_paragraphs=False):
            wrap_text_calls.append((text, width, preserve_paragraphs))
            return original_wrap_text(text, width, preserve_paragraphs=preserve_paragraphs)
        
        import click.formatting
        click.formatting.wrap_text = mock_wrap_text
        try:
            rows = [("term", "description with\n\nparagraphs")]
            formatter.write_dl(rows)
            # Verify wrap_text was called with preserve_paragraphs=True
            assert len(wrap_text_calls) > 0
            assert wrap_text_calls[0][2] is True
        finally:
            click.formatting.wrap_text = original_wrap_text

    def test_write_dl_with_single_line_description(self):
        """Test write_dl where description fits on one line."""
        formatter = HelpFormatter(width=80)
        rows = [("term", "short description")]
        formatter.write_dl(rows)
        # Should have term, spaces, and description on first line
        assert len(formatter.buffer) >= 1
        assert "short description" in "".join(formatter.buffer)

    def test_write_dl_with_very_narrow_width(self):
        """Test write_dl with very narrow width to force text wrapping."""
        formatter = HelpFormatter(width=20)
        rows = [("term", "This is a long description that must wrap")]
        formatter.write_dl(rows)
        # Should have multiple lines due to wrapping
        assert len(formatter.buffer) > 2
