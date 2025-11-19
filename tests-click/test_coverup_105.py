# file: src/click/src/click/_termui_impl.py:282-302
# asked: {"lines": [282, 283, 284, 285, 287, 288, 290, 295, 296, 298, 300, 302], "branches": [[284, 285], [284, 287], [287, 288], [287, 290], [295, 296], [295, 298]]}
# gained: {"lines": [282, 283, 284, 285, 287, 288, 290, 295, 296, 300, 302], "branches": [[284, 285], [284, 287], [287, 288], [287, 290], [295, 296]]}

import pytest
import time
from click._termui_impl import ProgressBar


class TestProgressBarMakeStep:
    def test_make_step_finishes_when_pos_exceeds_length(self):
        """Test that ProgressBar finishes when pos >= length"""
        bar = ProgressBar(range(10), length=5)
        bar.make_step(6)
        assert bar.finished is True
        assert bar.pos == 6

    def test_make_step_returns_early_when_less_than_1_second_since_last_eta(self, monkeypatch):
        """Test that make_step returns early when less than 1 second since last eta update"""
        bar = ProgressBar(range(10))
        bar.last_eta = time.time() - 0.5  # Less than 1 second ago
        
        # Mock time.time to return a value that keeps the condition true
        mock_time = time.time()
        monkeypatch.setattr(time, 'time', lambda: mock_time)
        
        # Store initial state
        initial_avg = bar.avg.copy()
        initial_eta_known = bar.eta_known
        
        bar.make_step(1)
        
        # Verify state didn't change (early return occurred)
        assert bar.avg == initial_avg
        assert bar.eta_known == initial_eta_known

    def test_make_step_updates_eta_with_nonzero_pos(self, monkeypatch):
        """Test that make_step updates eta calculations when pos > 0"""
        bar = ProgressBar(range(10), length=10)
        bar.pos = 5
        bar.start = time.time() - 10.0  # Started 10 seconds ago
        
        # Mock time.time to return a fixed value
        fixed_time = 1000.0
        monkeypatch.setattr(time, 'time', lambda: fixed_time)
        
        # Set last_eta to ensure we pass the 1-second check
        bar.last_eta = fixed_time - 2.0
        
        bar.make_step(1)
        
        # Verify eta calculations were updated
        assert bar.last_eta == fixed_time
        assert len(bar.avg) == 1
        assert bar.eta_known is True

    def test_make_step_updates_eta_with_zero_pos(self, monkeypatch):
        """Test that make_step updates eta calculations when pos == 0"""
        bar = ProgressBar(range(10), length=10)
        bar.pos = 0
        bar.start = time.time() - 5.0  # Started 5 seconds ago
        
        # Mock time.time to return a fixed value
        fixed_time = 1000.0
        monkeypatch.setattr(time, 'time', lambda: fixed_time)
        
        # Set last_eta to ensure we pass the 1-second check
        bar.last_eta = fixed_time - 2.0
        
        bar.make_step(1)
        
        # Verify eta calculations were updated
        assert bar.last_eta == fixed_time
        assert len(bar.avg) == 1
        assert bar.eta_known is True

    def test_make_step_rolling_average_maintains_max_7_elements(self, monkeypatch):
        """Test that the rolling average maintains at most 7 elements"""
        bar = ProgressBar(range(10), length=10)
        bar.pos = 1
        bar.avg = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]  # Already 7 elements
        
        # Mock time to ensure we pass the 1-second check
        fixed_time = 1000.0
        monkeypatch.setattr(time, 'time', lambda: fixed_time)
        bar.last_eta = fixed_time - 2.0
        bar.start = fixed_time - 10.0
        
        bar.make_step(1)
        
        # Should maintain at most 7 elements (keep last 6 + new one)
        assert len(bar.avg) == 7
        # The new avg should be the last 6 elements of the old avg plus the new step
        # step = (current_time - start) / pos = (1000 - 990) / 2 = 5.0
        assert bar.avg == [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 5.0]

    def test_make_step_with_no_length_sets_eta_known_false(self, monkeypatch):
        """Test that eta_known is False when length is None"""
        # Create ProgressBar with iterable that has no length hint
        class NoLengthIterable:
            def __iter__(self):
                return iter([1, 2, 3])
        
        bar = ProgressBar(NoLengthIterable())  # No length parameter
        bar.pos = 1
        
        # Mock time to ensure we pass the 1-second check
        fixed_time = 1000.0
        monkeypatch.setattr(time, 'time', lambda: fixed_time)
        bar.last_eta = fixed_time - 2.0
        
        bar.make_step(1)
        
        # With no length, eta_known should be False
        assert bar.eta_known is False
