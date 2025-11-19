# file: src/click/src/click/types.py:374-375
# asked: {"lines": [374, 375], "branches": []}
# gained: {"lines": [374, 375], "branches": []}

import pytest
from click.types import Choice


class TestChoiceRepr:
    def test_repr_with_choices(self):
        """Test that __repr__ returns the expected string format with choices."""
        choice_type = Choice(['option1', 'option2', 'option3'])
        result = repr(choice_type)
        expected = "Choice(['option1', 'option2', 'option3'])"
        assert result == expected

    def test_repr_with_empty_choices(self):
        """Test that __repr__ returns the expected string format with empty choices."""
        choice_type = Choice([])
        result = repr(choice_type)
        expected = "Choice([])"
        assert result == expected

    def test_repr_with_single_choice(self):
        """Test that __repr__ returns the expected string format with a single choice."""
        choice_type = Choice(['single_option'])
        result = repr(choice_type)
        expected = "Choice(['single_option'])"
        assert result == expected

    def test_repr_with_numeric_choices(self):
        """Test that __repr__ returns the expected string format with numeric choices."""
        choice_type = Choice([1, 2, 3])
        result = repr(choice_type)
        expected = "Choice([1, 2, 3])"
        assert result == expected

    def test_repr_with_mixed_type_choices(self):
        """Test that __repr__ returns the expected string format with mixed type choices."""
        choice_type = Choice(['string', 42, True, None])
        result = repr(choice_type)
        expected = "Choice(['string', 42, True, None])"
        assert result == expected
