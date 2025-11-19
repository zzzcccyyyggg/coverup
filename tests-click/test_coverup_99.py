# file: src/click/src/click/_termui_impl.py:304-328
# asked: {"lines": [304, 320, 321, 323, 325, 326, 327, 328], "branches": [[320, 321], [320, 323], [325, 0], [325, 326]]}
# gained: {"lines": [304, 320, 321, 323, 325, 326, 327, 328], "branches": [[320, 321], [320, 323], [325, 0], [325, 326]]}

import pytest
from click._termui_impl import ProgressBar
from io import StringIO

class TestProgressBarUpdate:
    def test_update_with_current_item(self):
        """Test that update sets current_item when provided."""
        file = StringIO()
        bar = ProgressBar(range(10), file=file, update_min_steps=1)
        bar.update(1, current_item="test_item")
        assert bar.current_item == "test_item"

    def test_update_without_current_item(self):
        """Test that update doesn't change current_item when not provided."""
        file = StringIO()
        bar = ProgressBar(range(10), file=file, update_min_steps=1)
        bar.current_item = "initial_item"
        bar.update(1)
        assert bar.current_item == "initial_item"

    def test_update_below_min_steps(self):
        """Test that update doesn't render when below update_min_steps."""
        file = StringIO()
        bar = ProgressBar(range(10), file=file, update_min_steps=5)
        initial_completed_intervals = bar._completed_intervals
        bar.update(3)
        assert bar._completed_intervals == initial_completed_intervals + 3
        # Should not have rendered since 3 < 5

    def test_update_at_min_steps(self):
        """Test that update renders when exactly at update_min_steps."""
        file = StringIO()
        bar = ProgressBar(range(10), file=file, update_min_steps=5)
        bar.update(5)
        assert bar._completed_intervals == 0  # Should be reset after render

    def test_update_above_min_steps(self):
        """Test that update renders when above update_min_steps."""
        file = StringIO()
        bar = ProgressBar(range(10), file=file, update_min_steps=5)
        bar.update(7)
        assert bar._completed_intervals == 0  # Should be reset after render

    def test_update_accumulates_below_threshold(self):
        """Test that multiple updates accumulate until reaching threshold."""
        file = StringIO()
        bar = ProgressBar(range(10), file=file, update_min_steps=5)
        bar.update(2)
        assert bar._completed_intervals == 2
        bar.update(2)
        assert bar._completed_intervals == 4
        bar.update(1)  # This should trigger render
        assert bar._completed_intervals == 0

    def test_update_with_current_item_and_rendering(self):
        """Test update with current_item that triggers rendering."""
        file = StringIO()
        bar = ProgressBar(range(10), file=file, update_min_steps=1)
        bar.update(1, current_item="rendering_item")
        assert bar.current_item == "rendering_item"
        assert bar._completed_intervals == 0  # Should be reset after render
