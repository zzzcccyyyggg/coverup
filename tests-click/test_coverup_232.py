# file: src/click/src/click/formatting.py:24-28
# asked: {"lines": [24, 27, 28], "branches": [[27, 0], [27, 28]]}
# gained: {"lines": [24, 27, 28], "branches": [[27, 0], [27, 28]]}

import pytest
import collections.abc as cabc
from click.formatting import iter_rows

class TestIterRows:
    def test_iter_rows_with_insufficient_columns(self):
        """Test iter_rows when rows have fewer columns than col_count."""
        rows = [("col1", "col2")]
        col_count = 4
        result = list(iter_rows(rows, col_count))
        expected = [("col1", "col2", "", "")]
        assert result == expected

    def test_iter_rows_with_exact_columns(self):
        """Test iter_rows when rows have exactly col_count columns."""
        rows = [("col1", "col2", "col3", "col4")]
        col_count = 4
        result = list(iter_rows(rows, col_count))
        expected = [("col1", "col2", "col3", "col4")]
        assert result == expected

    def test_iter_rows_with_empty_rows(self):
        """Test iter_rows with empty rows list."""
        rows = []
        col_count = 3
        result = list(iter_rows(rows, col_count))
        expected = []
        assert result == expected

    def test_iter_rows_with_single_column(self):
        """Test iter_rows when col_count is 1."""
        rows = [("col1",)]
        col_count = 1
        result = list(iter_rows(rows, col_count))
        expected = [("col1",)]
        assert result == expected

    def test_iter_rows_with_more_columns_than_needed(self):
        """Test iter_rows when rows have more columns than col_count."""
        rows = [("col1", "col2", "col3")]
        col_count = 2
        result = list(iter_rows(rows, col_count))
        expected = [("col1", "col2", "col3")]
        assert result == expected
