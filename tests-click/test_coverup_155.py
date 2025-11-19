# file: src/click/src/click/_termui_impl.py:154-158
# asked: {"lines": [154, 155, 156, 157, 158], "branches": [[156, 157], [156, 158]]}
# gained: {"lines": [154, 155, 156, 157, 158], "branches": [[156, 157], [156, 158]]}

import pytest
from click._termui_impl import ProgressBar


class TestProgressBarTimePerIteration:
    def test_time_per_iteration_when_avg_is_empty(self):
        """Test time_per_iteration property when avg is empty (returns 0.0)"""
        progress_bar = ProgressBar(range(5))
        progress_bar.avg = []
        
        result = progress_bar.time_per_iteration
        
        assert result == 0.0

    def test_time_per_iteration_when_avg_has_values(self):
        """Test time_per_iteration property when avg has values (calculates average)"""
        progress_bar = ProgressBar(range(5))
        progress_bar.avg = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        result = progress_bar.time_per_iteration
        
        assert result == 3.0  # (1+2+3+4+5)/5 = 3.0
