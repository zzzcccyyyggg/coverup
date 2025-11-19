# file: src/click/src/click/_termui_impl.py:330-333
# asked: {"lines": [330, 331, 332, 333], "branches": []}
# gained: {"lines": [330, 331, 332, 333], "branches": []}

import pytest
from click._termui_impl import ProgressBar


class TestProgressBarFinish:
    def test_finish_sets_correct_state(self):
        """Test that finish() method sets the correct state variables."""
        # Create a progress bar with a simple iterable
        progress_bar = ProgressBar(range(5))
        
        # Verify initial state
        assert progress_bar.eta_known is False
        assert progress_bar.current_item is None
        assert progress_bar.finished is False
        
        # Call finish method
        progress_bar.finish()
        
        # Verify state after finish
        assert progress_bar.eta_known is False
        assert progress_bar.current_item is None
        assert progress_bar.finished is True
