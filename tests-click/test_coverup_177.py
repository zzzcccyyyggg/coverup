# file: src/click/src/click/_termui_impl.py:181-185
# asked: {"lines": [181, 182, 183, 184, 185], "branches": [[183, 184], [183, 185]]}
# gained: {"lines": [181, 182, 183, 184, 185], "branches": [[183, 184], [183, 185]]}

import pytest
from click._termui_impl import ProgressBar

class TestProgressBarFormatPos:
    def test_format_pos_without_length(self):
        """Test format_pos when length is None"""
        # Create a custom iterable that doesn't support len() or __length_hint__
        class CustomIterable:
            def __init__(self, items):
                self.items = items
                self.index = 0
            
            def __iter__(self):
                return self
            
            def __next__(self):
                if self.index >= len(self.items):
                    raise StopIteration
                item = self.items[self.index]
                self.index += 1
                return item
        
        bar = ProgressBar(iterable=CustomIterable([1, 2, 3]), length=None)
        bar.pos = 5
        result = bar.format_pos()
        assert result == "5"
    
    def test_format_pos_with_length(self):
        """Test format_pos when length is provided"""
        bar = ProgressBar(iterable=[1, 2, 3], length=10)
        bar.pos = 5
        result = bar.format_pos()
        assert result == "5/10"
