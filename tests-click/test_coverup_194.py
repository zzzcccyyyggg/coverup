# file: src/click/src/click/exceptions.py:19-23
# asked: {"lines": [19, 20, 21, 23], "branches": [[20, 21], [20, 23]]}
# gained: {"lines": [19, 20, 21, 23], "branches": [[20, 21], [20, 23]]}

import pytest
import collections.abc as cabc
from click.exceptions import _join_param_hints


class TestJoinParamHints:
    def test_join_param_hints_with_none(self):
        """Test _join_param_hints with None input."""
        result = _join_param_hints(None)
        assert result is None

    def test_join_param_hints_with_string(self):
        """Test _join_param_hints with string input."""
        result = _join_param_hints("test_string")
        assert result == "test_string"

    def test_join_param_hints_with_sequence(self):
        """Test _join_param_hints with sequence input."""
        result = _join_param_hints(["option1", "option2", "option3"])
        expected = "'option1' / 'option2' / 'option3'"
        assert result == expected

    def test_join_param_hints_with_empty_sequence(self):
        """Test _join_param_hints with empty sequence input."""
        result = _join_param_hints([])
        expected = ""
        assert result == expected

    def test_join_param_hints_with_tuple_sequence(self):
        """Test _join_param_hints with tuple sequence input."""
        result = _join_param_hints(("arg1", "arg2"))
        expected = "'arg1' / 'arg2'"
        assert result == expected
