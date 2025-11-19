# file: src/click/src/click/formatting.py:14-21
# asked: {"lines": [14, 15, 17, 18, 19, 21], "branches": [[17, 18], [17, 21], [18, 17], [18, 19]]}
# gained: {"lines": [14, 15, 17, 18, 19, 21], "branches": [[17, 18], [17, 21], [18, 17], [18, 19]]}

import pytest
from click.formatting import measure_table
from click._compat import term_len


class TestMeasureTable:
    def test_measure_table_empty_rows(self):
        """Test measure_table with empty rows."""
        result = measure_table([])
        assert result == ()

    def test_measure_table_single_row_single_column(self):
        """Test measure_table with single row and single column."""
        rows = [("hello",)]
        result = measure_table(rows)
        assert result == (term_len("hello"),)

    def test_measure_table_single_row_multiple_columns(self):
        """Test measure_table with single row and multiple columns."""
        rows = [("hello", "world")]
        result = measure_table(rows)
        assert result == (term_len("hello"), term_len("world"))

    def test_measure_table_multiple_rows_same_columns(self):
        """Test measure_table with multiple rows and same number of columns."""
        rows = [
            ("hello", "world"),
            ("test", "data")
        ]
        result = measure_table(rows)
        assert result == (term_len("hello"), term_len("world"))

    def test_measure_table_multiple_rows_different_widths(self):
        """Test measure_table with multiple rows where columns have different widths."""
        rows = [
            ("short", "very_long_column"),
            ("very_long_text", "short")
        ]
        result = measure_table(rows)
        assert result == (term_len("very_long_text"), term_len("very_long_column"))

    def test_measure_table_with_ansi_sequences(self, monkeypatch):
        """Test measure_table with ANSI sequences that should be stripped."""
        # Mock term_len to simulate ANSI sequence stripping
        def mock_term_len(text):
            # Simulate stripping ANSI sequences by removing any brackets
            cleaned = text.replace('[', '').replace(']', '')
            return len(cleaned)
        
        monkeypatch.setattr('click.formatting.term_len', mock_term_len)
        
        rows = [
            ("[red]hello[/red]", "normal"),
            ("test", "[bold]world[/bold]")
        ]
        result = measure_table(rows)
        # Calculate expected values using the mocked term_len
        expected_col1 = max(mock_term_len("[red]hello[/red]"), mock_term_len("test"))
        expected_col2 = max(mock_term_len("normal"), mock_term_len("[bold]world[/bold]"))
        assert result == (expected_col1, expected_col2)

    def test_measure_table_uneven_rows(self):
        """Test measure_table with rows having different number of columns."""
        rows = [
            ("col1", "col2", "col3"),
            ("a", "b"),
            ("x", "y", "z", "w")  # Extra column
        ]
        result = measure_table(rows)
        # Should handle different column counts gracefully
        assert len(result) == 4  # Maximum number of columns across all rows
        assert result[0] == term_len("col1")
        assert result[1] == term_len("col2") 
        assert result[2] == term_len("col3")
        assert result[3] == term_len("w")
