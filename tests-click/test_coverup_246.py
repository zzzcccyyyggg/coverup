# file: src/click/src/click/types.py:258-262
# asked: {"lines": [258, 259, 261, 262], "branches": []}
# gained: {"lines": [258, 259, 261, 262], "branches": []}

import pytest
import click
from click.types import Choice


class TestChoiceInit:
    def test_choice_init_with_empty_iterable(self):
        """Test that Choice can be initialized with an empty iterable."""
        choice_type = Choice([])
        assert choice_type.choices == ()
        assert choice_type.case_sensitive is True

    def test_choice_init_with_list(self):
        """Test that Choice can be initialized with a list."""
        choices = ['option1', 'option2', 'option3']
        choice_type = Choice(choices)
        assert choice_type.choices == tuple(choices)
        assert choice_type.case_sensitive is True

    def test_choice_init_with_tuple(self):
        """Test that Choice can be initialized with a tuple."""
        choices = ('a', 'b', 'c')
        choice_type = Choice(choices)
        assert choice_type.choices == choices
        assert choice_type.case_sensitive is True

    def test_choice_init_with_set(self):
        """Test that Choice can be initialized with a set."""
        choices = {'x', 'y', 'z'}
        choice_type = Choice(choices)
        # The order might be different due to set being unordered
        assert set(choice_type.choices) == choices
        assert choice_type.case_sensitive is True

    def test_choice_init_with_generator(self):
        """Test that Choice can be initialized with a generator."""
        def choice_generator():
            yield 'first'
            yield 'second'
            yield 'third'
        
        choice_type = Choice(choice_generator())
        assert choice_type.choices == ('first', 'second', 'third')
        assert choice_type.case_sensitive is True

    def test_choice_init_case_sensitive_false(self):
        """Test that Choice can be initialized with case_sensitive=False."""
        choices = ['Option1', 'Option2']
        choice_type = Choice(choices, case_sensitive=False)
        assert choice_type.choices == tuple(choices)
        assert choice_type.case_sensitive is False

    def test_choice_init_case_sensitive_true_explicit(self):
        """Test that Choice can be initialized with case_sensitive=True explicitly."""
        choices = ['A', 'B', 'C']
        choice_type = Choice(choices, case_sensitive=True)
        assert choice_type.choices == tuple(choices)
        assert choice_type.case_sensitive is True
