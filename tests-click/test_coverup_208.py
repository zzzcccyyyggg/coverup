# file: src/click/src/click/core.py:2017-2024
# asked: {"lines": [2017, 2021, 2022, 2024], "branches": [[2021, 2022], [2021, 2024]]}
# gained: {"lines": [2017, 2021, 2022, 2024], "branches": [[2021, 2022], [2021, 2024]]}

import pytest
import collections.abc as cabc
import typing as t
from click.core import _check_iter


class TestCheckIter:
    def test_check_iter_with_string_raises_type_error(self):
        """Test that _check_iter raises TypeError when given a string."""
        with pytest.raises(TypeError):
            _check_iter("test_string")
    
    def test_check_iter_with_list_returns_iterator(self):
        """Test that _check_iter returns an iterator for a list."""
        test_list = [1, 2, 3]
        result = _check_iter(test_list)
        assert isinstance(result, cabc.Iterator)
        assert list(result) == test_list
    
    def test_check_iter_with_tuple_returns_iterator(self):
        """Test that _check_iter returns an iterator for a tuple."""
        test_tuple = (1, 2, 3)
        result = _check_iter(test_tuple)
        assert isinstance(result, cabc.Iterator)
        assert list(result) == list(test_tuple)
    
    def test_check_iter_with_set_returns_iterator(self):
        """Test that _check_iter returns an iterator for a set."""
        test_set = {1, 2, 3}
        result = _check_iter(test_set)
        assert isinstance(result, cabc.Iterator)
        assert set(result) == test_set
    
    def test_check_iter_with_dict_returns_iterator(self):
        """Test that _check_iter returns an iterator for a dict."""
        test_dict = {"a": 1, "b": 2}
        result = _check_iter(test_dict)
        assert isinstance(result, cabc.Iterator)
        assert list(result) == list(test_dict)
