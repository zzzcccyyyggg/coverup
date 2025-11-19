# file: src/click/src/click/_termui_impl.py:142-146
# asked: {"lines": [142, 143, 144, 145, 146], "branches": [[143, 144], [143, 145]]}
# gained: {"lines": [142, 143, 144, 145, 146], "branches": [[143, 144], [143, 145]]}

import pytest
from io import StringIO
from unittest.mock import Mock, patch
from click._termui_impl import ProgressBar, AFTER_BAR


class TestProgressBarRenderFinish:
    def test_render_finish_hidden(self):
        """Test render_finish when hidden is True"""
        file = StringIO()
        bar = ProgressBar(range(5), hidden=True, file=file)
        bar.render_finish()
        assert file.getvalue() == ""

    def test_render_finish_not_atty(self):
        """Test render_finish when not atty"""
        file = StringIO()
        with patch('click._termui_impl.isatty', return_value=False):
            bar = ProgressBar(range(5), file=file)
            bar.render_finish()
            assert file.getvalue() == ""

    def test_render_finish_visible_and_atty(self):
        """Test render_finish when visible and atty"""
        file = StringIO()
        with patch('click._termui_impl.isatty', return_value=True):
            bar = ProgressBar(range(5), file=file)
            bar.render_finish()
            assert file.getvalue() == AFTER_BAR
