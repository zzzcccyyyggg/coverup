# file: src/click/src/click/_termui_impl.py:160-164
# asked: {"lines": [160, 161, 162, 163, 164], "branches": [[162, 163], [162, 164]]}
# gained: {"lines": [160, 161, 162, 163, 164], "branches": [[162, 163], [162, 164]]}

import pytest
from click._termui_impl import ProgressBar
import time

class TestProgressBarETA:
    def test_eta_with_length_and_not_finished(self):
        """Test that eta property returns calculated value when length is set and not finished."""
        # Create a progress bar with a known length
        progress_bar = ProgressBar(range(10), length=10)
        
        # Simulate some progress
        progress_bar.pos = 3
        progress_bar.avg = [1.0, 1.0, 1.0]  # Simulate time per iteration
        
        # Verify eta is calculated correctly
        expected_eta = progress_bar.time_per_iteration * (progress_bar.length - progress_bar.pos)
        assert progress_bar.eta == expected_eta
        assert progress_bar.eta > 0.0

    def test_eta_with_no_length(self):
        """Test that eta property returns 0.0 when length is None."""
        # Create a progress bar with an iterable that has unknown length
        # Use an iterator that doesn't support len() to get length=None
        def custom_iterator():
            yield 1
            yield 2
            yield 3
        
        progress_bar = ProgressBar(custom_iterator())
        
        # Verify eta returns 0.0 when length is None
        assert progress_bar.eta == 0.0

    def test_eta_when_finished(self):
        """Test that eta property returns 0.0 when progress bar is finished."""
        # Create a progress bar and mark it as finished
        progress_bar = ProgressBar(range(5), length=5)
        progress_bar.finished = True
        
        # Verify eta returns 0.0 when finished
        assert progress_bar.eta == 0.0

    def test_eta_with_length_none_and_finished(self):
        """Test that eta property returns 0.0 when length is None and finished."""
        # Create a progress bar with an iterable that has unknown length
        def custom_iterator():
            yield 1
            yield 2
            yield 3
        
        progress_bar = ProgressBar(custom_iterator())
        progress_bar.finished = True
        
        # Verify eta returns 0.0
        assert progress_bar.eta == 0.0
