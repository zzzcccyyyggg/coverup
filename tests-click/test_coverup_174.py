# file: src/click/src/click/_termui_impl.py:148-152
# asked: {"lines": [148, 149, 150, 151, 152], "branches": [[150, 151], [150, 152]]}
# gained: {"lines": [148, 149, 150, 151, 152], "branches": [[150, 151], [150, 152]]}

import pytest
from click._termui_impl import ProgressBar


class TestProgressBarPct:
    def test_pct_finished(self):
        """Test pct property when progress bar is finished."""
        progress_bar = ProgressBar(range(10))
        progress_bar.finished = True
        
        assert progress_bar.pct == 1.0

    def test_pct_zero_length(self):
        """Test pct property when length is 0."""
        progress_bar = ProgressBar([], length=0)
        progress_bar.pos = 5
        
        # When length is 0, the calculation becomes: min(5 / (float(0) or 1), 1.0)
        # float(0) or 1 = 1, so 5 / 1 = 5.0, then min(5.0, 1.0) = 1.0
        assert progress_bar.pct == 1.0

    def test_pct_none_length(self):
        """Test pct property when length is None."""
        progress_bar = ProgressBar([])
        progress_bar.pos = 5
        progress_bar.length = None
        
        # When length is None, the calculation becomes: min(5 / (float(None) or 1), 1.0)
        # float(None) or 1 = 1, so 5 / 1 = 5.0, then min(5.0, 1.0) = 1.0
        assert progress_bar.pct == 1.0

    def test_pct_normal_case(self):
        """Test pct property in normal case."""
        progress_bar = ProgressBar(range(10))
        progress_bar.pos = 5
        progress_bar.length = 10
        
        assert progress_bar.pct == 0.5

    def test_pct_exceeds_one(self):
        """Test pct property when pos exceeds length."""
        progress_bar = ProgressBar(range(10))
        progress_bar.pos = 15
        progress_bar.length = 10
        
        assert progress_bar.pct == 1.0
