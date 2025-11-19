# file: src/click/src/click/_termui_impl.py:128-132
# asked: {"lines": [128, 129, 130, 131, 132], "branches": [[129, 130], [129, 131]]}
# gained: {"lines": [128, 129, 130, 131, 132], "branches": [[129, 130], [129, 131]]}

import pytest
from click._termui_impl import ProgressBar
from io import StringIO

def test_progressbar_iter_not_entered():
    """Test that __iter__ raises RuntimeError when not entered."""
    progress_bar = ProgressBar(range(5))
    with pytest.raises(RuntimeError, match="You need to use progress bars in a with block."):
        iter(progress_bar)

def test_progressbar_iter_entered():
    """Test that __iter__ works correctly when entered."""
    with ProgressBar(range(3), file=StringIO()) as progress_bar:
        iterator = iter(progress_bar)
        items = list(iterator)
        assert items == [0, 1, 2]
