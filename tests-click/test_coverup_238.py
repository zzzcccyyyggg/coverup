# file: src/click/src/click/_termui_impl.py:115-118
# asked: {"lines": [115, 116, 117, 118], "branches": []}
# gained: {"lines": [115, 116, 117, 118], "branches": []}

import pytest
from click._termui_impl import ProgressBar
from io import StringIO

def test_progressbar_context_manager_enters_and_renders():
    """Test that ProgressBar context manager sets entered flag and renders progress."""
    file = StringIO()
    # Set hidden=False to ensure render_progress actually renders
    with ProgressBar(range(5), file=file, hidden=False) as bar:
        assert bar.entered is True
        # Verify that render_progress was called by checking file output
        file_content = file.getvalue()
        # The progress bar should have been rendered (may contain various characters)
        assert len(file_content) > 0

def test_progressbar_context_manager_returns_self():
    """Test that ProgressBar context manager returns self."""
    file = StringIO()
    with ProgressBar(range(5), file=file) as bar:
        assert isinstance(bar, ProgressBar)
        assert bar.length == 5
