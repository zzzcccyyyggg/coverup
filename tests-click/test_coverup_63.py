# file: src/click/src/click/_termui_impl.py:166-179
# asked: {"lines": [166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 178, 179], "branches": [[167, 168], [167, 179], [175, 176], [175, 178]]}
# gained: {"lines": [166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 178, 179], "branches": [[167, 168], [167, 179], [175, 176], [175, 178]]}

import pytest
from click._termui_impl import ProgressBar

class TestProgressBarFormatEta:
    def test_format_eta_when_eta_known_with_days(self):
        """Test format_eta when eta_known is True and eta requires days formatting."""
        progress_bar = ProgressBar(range(100))
        progress_bar.eta_known = True
        # Mock the eta property to return a value that requires days formatting
        # 90061 seconds = 1 day, 1 hour, 1 minute, 1 second
        progress_bar.pos = 0
        progress_bar.length = 100
        progress_bar.finished = False
        progress_bar.avg = [900.61]  # time_per_iteration = 900.61 seconds
        
        result = progress_bar.format_eta()
        
        assert result == "1d 01:01:01"
    
    def test_format_eta_when_eta_known_without_days(self):
        """Test format_eta when eta_known is True and eta doesn't require days formatting."""
        progress_bar = ProgressBar(range(100))
        progress_bar.eta_known = True
        # Mock the eta property to return a value that doesn't require days formatting
        # 3661 seconds = 1 hour, 1 minute, 1 second
        progress_bar.pos = 0
        progress_bar.length = 100
        progress_bar.finished = False
        progress_bar.avg = [36.61]  # time_per_iteration = 36.61 seconds
        
        result = progress_bar.format_eta()
        
        assert result == "01:01:01"
    
    def test_format_eta_when_eta_unknown(self):
        """Test format_eta when eta_known is False."""
        progress_bar = ProgressBar([])
        progress_bar.eta_known = False
        
        result = progress_bar.format_eta()
        
        assert result == ""
