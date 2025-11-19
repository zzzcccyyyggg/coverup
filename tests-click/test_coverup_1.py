# file: src/click/src/click/parser.py:51-108
# asked: {"lines": [51, 63, 64, 65, 66, 68, 69, 70, 71, 73, 74, 75, 77, 78, 80, 81, 83, 84, 85, 86, 90, 91, 93, 94, 95, 96, 98, 99, 103, 104, 105, 106, 108], "branches": [[70, 71], [70, 73], [77, 78], [77, 103], [80, 81], [80, 83], [83, 84], [83, 85], [85, 86], [85, 94], [90, 91], [90, 93], [94, 77], [94, 95], [95, 96], [95, 98], [103, 104], [103, 108]]}
# gained: {"lines": [51, 63, 64, 65, 66, 68, 69, 70, 71, 73, 74, 75, 77, 78, 80, 81, 83, 84, 85, 86, 90, 91, 93, 94, 95, 96, 98, 99, 103, 104, 105, 106, 108], "branches": [[70, 71], [70, 73], [77, 78], [77, 103], [80, 81], [80, 83], [83, 84], [83, 85], [85, 86], [85, 94], [90, 91], [90, 93], [94, 95], [95, 96], [95, 98], [103, 104], [103, 108]]}

import pytest
from click.parser import _unpack_args
from click._utils import UNSET


def test_unpack_args_with_none_nargs():
    """Test that None nargs are skipped."""
    result, remaining = _unpack_args(['a', 'b'], [None, 1])
    assert result == ('a',)
    assert remaining == ['b']


def test_unpack_args_with_multiple_args():
    """Test nargs > 1."""
    result, remaining = _unpack_args(['a', 'b', 'c'], [2])
    assert result == (('a', 'b'),)
    assert remaining == ['c']


def test_unpack_args_with_multiple_args_reversed():
    """Test nargs > 1 with reversed fetching."""
    result, remaining = _unpack_args(['a', 'b', 'c', 'd'], [-1, 2])
    assert result == (('a', 'b'), ('c', 'd'))
    assert remaining == []


def test_unpack_args_with_negative_nargs():
    """Test nargs < 0 (wildcard)."""
    result, remaining = _unpack_args(['a', 'b', 'c'], [-1])
    assert result == (('a', 'b', 'c'),)
    assert remaining == []


def test_unpack_args_with_negative_nargs_and_remaining():
    """Test nargs < 0 with additional nargs after."""
    result, remaining = _unpack_args(['a', 'b', 'c', 'd'], [-1, 1])
    assert result == (('a', 'b', 'c'), 'd')
    assert remaining == []


def test_unpack_args_with_multiple_negative_nargs_raises():
    """Test that two negative nargs raises TypeError."""
    with pytest.raises(TypeError, match="Cannot have two nargs < 0"):
        _unpack_args(['a', 'b'], [-1, -1])


def test_unpack_args_with_insufficient_args():
    """Test when there are insufficient arguments."""
    result, remaining = _unpack_args(['a'], [2])
    assert result == (('a', UNSET),)
    assert remaining == []


def test_unpack_args_with_insufficient_args_reversed():
    """Test when there are insufficient arguments with reversed fetching."""
    result, remaining = _unpack_args(['a', 'b'], [1, -1, 2])
    assert result == ('a', (), (UNSET, 'b'))
    assert remaining == []
