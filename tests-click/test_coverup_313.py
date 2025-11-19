# file: src/click/src/click/core.py:93-94
# asked: {"lines": [93, 94], "branches": []}
# gained: {"lines": [93, 94], "branches": []}

import pytest
from click.core import batch

def test_batch_empty_iterable():
    """Test batch function with empty iterable."""
    result = batch([], 3)
    assert result == []

def test_batch_single_element():
    """Test batch function with single element."""
    result = batch([1], 3)
    assert result == []

def test_batch_exact_multiple():
    """Test batch function with iterable length exactly divisible by batch_size."""
    result = batch([1, 2, 3, 4, 5, 6], 3)
    assert result == [(1, 2, 3), (4, 5, 6)]

def test_batch_partial_final_batch():
    """Test batch function with iterable length not divisible by batch_size."""
    result = batch([1, 2, 3, 4, 5], 3)
    assert result == [(1, 2, 3)]

def test_batch_larger_batch_size():
    """Test batch function with batch_size larger than iterable length."""
    result = batch([1, 2], 5)
    assert result == []

def test_batch_with_string():
    """Test batch function with string iterable."""
    result = batch("abcdef", 2)
    assert result == [('a', 'b'), ('c', 'd'), ('e', 'f')]

def test_batch_with_tuple():
    """Test batch function with tuple iterable."""
    result = batch((1, 2, 3, 4), 2)
    assert result == [(1, 2), (3, 4)]

def test_batch_with_generator():
    """Test batch function with generator iterable."""
    def gen():
        yield from range(4)
    result = batch(gen(), 2)
    assert result == [(0, 1), (2, 3)]
