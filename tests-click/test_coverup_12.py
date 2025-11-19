# file: src/click/src/click/_termui_impl.py:236-280
# asked: {"lines": [236, 237, 238, 240, 242, 243, 244, 245, 247, 249, 250, 252, 253, 254, 255, 256, 257, 258, 259, 260, 262, 263, 264, 266, 267, 268, 269, 270, 272, 273, 274, 277, 278, 279, 280], "branches": [[237, 238], [237, 240], [240, 242], [240, 247], [242, 243], [242, 245], [249, 250], [249, 262], [256, 257], [256, 260], [263, 264], [263, 266], [269, 270], [269, 272], [277, 0], [277, 278]]}
# gained: {"lines": [236, 237, 238, 240, 242, 243, 244, 245, 247, 249, 250, 252, 253, 254, 255, 256, 257, 258, 259, 260, 262, 263, 264, 266, 267, 268, 269, 270, 272, 273, 274, 277, 278, 279, 280], "branches": [[237, 238], [237, 240], [240, 242], [240, 247], [242, 243], [242, 245], [249, 250], [249, 262], [256, 257], [263, 264], [263, 266], [269, 270], [269, 272], [277, 0], [277, 278]]}

import pytest
from click._termui_impl import ProgressBar, BEFORE_BAR
from click._compat import term_len
from click.utils import echo
from unittest.mock import Mock, patch
import io

class TestProgressBar:
    def test_render_progress_hidden(self):
        """Test that render_progress returns early when hidden is True"""
        bar = ProgressBar(None, 100, show_percent=False)
        bar.hidden = True
        bar.render_progress()
        # No assertion needed - just verifying no exception when hidden

    def test_render_progress_non_tty_label_change(self):
        """Test render_progress for non-TTY when label changes"""
        mock_file = io.StringIO()
        bar = ProgressBar(None, 100, show_percent=False, file=mock_file)
        bar._is_atty = False
        bar._last_line = "old_label"
        bar.label = "new_label"
        
        bar.render_progress()
        
        assert bar._last_line == "new_label"
        assert mock_file.getvalue() == "new_label\n"

    def test_render_progress_non_tty_label_unchanged(self):
        """Test render_progress for non-TTY when label doesn't change"""
        mock_file = io.StringIO()
        bar = ProgressBar(None, 100, show_percent=False, file=mock_file)
        bar._is_atty = False
        bar._last_line = "same_label"
        bar.label = "same_label"
        
        bar.render_progress()
        
        assert bar._last_line == "same_label"
        assert mock_file.getvalue() == ""

    def test_render_progress_autowidth_terminal_resize(self, monkeypatch):
        """Test render_progress with autowidth when terminal is resized smaller"""
        mock_file = io.StringIO()
        bar = ProgressBar(None, 100, show_percent=False, file=mock_file)
        bar._is_atty = True
        bar.autowidth = True
        bar.width = 50
        bar.max_width = 40
        
        # Mock shutil.get_terminal_size to return smaller terminal
        mock_size = Mock()
        mock_size.columns = 30
        monkeypatch.setattr("shutil.get_terminal_size", lambda: mock_size)
        
        # Mock format_progress_line to return a line with known length
        bar.format_progress_line = Mock(return_value="progress")
        
        bar.render_progress()
        
        assert bar.width == 30 - term_len("progress")
        assert bar.max_width == 30 - term_len("progress")

    def test_render_progress_max_width_adjustment(self):
        """Test render_progress when max_width needs adjustment"""
        mock_file = io.StringIO()
        bar = ProgressBar(None, 100, show_percent=False, file=mock_file)
        bar._is_atty = True
        bar.autowidth = False
        bar.max_width = 10
        
        # Mock format_progress_line to return a longer line
        bar.format_progress_line = Mock(return_value="this_is_a_longer_line")
        
        bar.render_progress()
        
        assert bar.max_width == term_len("this_is_a_longer_line")

    def test_render_progress_line_changed(self):
        """Test render_progress when the rendered line changes"""
        mock_file = io.StringIO()
        bar = ProgressBar(None, 100, show_percent=False, file=mock_file)
        bar._is_atty = True
        bar.autowidth = False
        bar._last_line = "old_line"
        bar.width = 20
        bar.max_width = None
        
        # Mock format_progress_line to return a different line
        bar.format_progress_line = Mock(return_value="new_line")
        
        bar.render_progress()
        
        # The line should include BEFORE_BAR and padding
        expected_line = BEFORE_BAR + "new_line" + " " * (20 - term_len("new_line"))
        assert bar._last_line == expected_line
        assert mock_file.getvalue() != ""

    def test_render_progress_line_unchanged(self):
        """Test render_progress when the rendered line doesn't change"""
        mock_file = io.StringIO()
        bar = ProgressBar(None, 100, show_percent=False, file=mock_file)
        bar._is_atty = True
        bar.autowidth = False
        bar.width = 20
        bar.max_width = None
        
        # Create the expected line that will be generated
        bar.format_progress_line = Mock(return_value="same_line")
        expected_line = BEFORE_BAR + "same_line" + " " * (20 - term_len("same_line"))
        bar._last_line = expected_line
        
        bar.render_progress()
        
        # The line should remain unchanged and no output should be written
        assert bar._last_line == expected_line
        assert mock_file.getvalue() == ""
