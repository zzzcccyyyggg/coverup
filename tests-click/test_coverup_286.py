# file: src/click/src/click/_termui_impl.py:134-140
# asked: {"lines": [134, 140], "branches": []}
# gained: {"lines": [134, 140], "branches": []}

import pytest
from click._termui_impl import ProgressBar
from io import StringIO

def test_progress_bar_next_method():
    """Test that __next__ method correctly calls next(iter(self))"""
    # Create a simple iterable for testing
    test_items = [1, 2, 3]
    
    # Create a ProgressBar with the test items
    with ProgressBar(test_items, file=StringIO()) as bar:
        # Get the iterator
        iterator = iter(bar)
        
        # Test that __next__ returns the same as next(iter(self))
        assert next(iterator) == 1
        assert next(iterator) == 2
        assert next(iterator) == 3
        
        # Verify that calling __next__ directly works the same
        # Reset the bar for this test
        with ProgressBar(test_items, file=StringIO()) as bar2:
            # Test __next__ method directly
            assert bar2.__next__() == 1
            assert bar2.__next__() == 2
            assert bar2.__next__() == 3

def test_progress_bar_next_raises_stop_iteration():
    """Test that __next__ raises StopIteration when exhausted"""
    test_items = [1]
    
    with ProgressBar(test_items, file=StringIO()) as bar:
        # Consume the only item
        assert bar.__next__() == 1
        
        # Now __next__ should raise StopIteration
        with pytest.raises(StopIteration):
            bar.__next__()

def test_progress_bar_next_with_empty_iterable():
    """Test __next__ with empty iterable"""
    with ProgressBar([], file=StringIO()) as bar:
        # Should immediately raise StopIteration
        with pytest.raises(StopIteration):
            bar.__next__()
