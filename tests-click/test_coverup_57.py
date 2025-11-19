# file: src/click/src/click/formatting.py:116-133
# asked: {"lines": [116, 118, 119, 120, 122, 123, 124, 125, 126, 128, 129, 130, 131, 132, 133], "branches": [[123, 124], [123, 125], [125, 126], [125, 131], [129, 130], [129, 131]]}
# gained: {"lines": [116, 118, 119, 120, 122, 123, 124, 125, 126, 128, 129, 130, 131, 132, 133], "branches": [[123, 124], [123, 125], [125, 126], [125, 131], [129, 130], [129, 131]]}

import pytest
import shutil
from unittest.mock import Mock
from click.formatting import HelpFormatter


class TestHelpFormatterInit:
    def test_init_with_width_none_and_forced_width_none(self, monkeypatch):
        # Mock shutil.get_terminal_size to return a known value
        mock_terminal_size = Mock()
        mock_terminal_size.columns = 100
        monkeypatch.setattr(shutil, 'get_terminal_size', lambda: mock_terminal_size)
        
        # Mock FORCED_WIDTH to be None
        monkeypatch.setattr('click.formatting.FORCED_WIDTH', None)
        
        formatter = HelpFormatter(width=None, max_width=80)
        
        # Verify the width calculation: max(min(100, 80) - 2, 50) = max(78, 50) = 78
        assert formatter.width == 78
        assert formatter.indent_increment == 2
        assert formatter.current_indent == 0
        assert formatter.buffer == []

    def test_init_with_width_none_and_forced_width_set(self, monkeypatch):
        # Mock FORCED_WIDTH to be a specific value
        monkeypatch.setattr('click.formatting.FORCED_WIDTH', 60)
        
        formatter = HelpFormatter(width=None, max_width=80)
        
        # Should use FORCED_WIDTH directly when it's not None
        assert formatter.width == 60
        assert formatter.indent_increment == 2
        assert formatter.current_indent == 0
        assert formatter.buffer == []

    def test_init_with_custom_width(self):
        formatter = HelpFormatter(width=70, max_width=90)
        
        # Should use the provided width directly
        assert formatter.width == 70
        assert formatter.indent_increment == 2
        assert formatter.current_indent == 0
        assert formatter.buffer == []

    def test_init_with_custom_indent_increment(self):
        formatter = HelpFormatter(indent_increment=4, width=65)
        
        assert formatter.indent_increment == 4
        assert formatter.width == 65
        assert formatter.current_indent == 0
        assert formatter.buffer == []

    def test_init_with_max_width_none(self):
        formatter = HelpFormatter(width=75, max_width=None)
        
        # max_width should default to 80 when None
        assert formatter.width == 75
        assert formatter.indent_increment == 2
        assert formatter.current_indent == 0
        assert formatter.buffer == []

    def test_init_width_calculation_with_small_terminal(self, monkeypatch):
        # Mock terminal size to be smaller than minimum
        mock_terminal_size = Mock()
        mock_terminal_size.columns = 40
        monkeypatch.setattr(shutil, 'get_terminal_size', lambda: mock_terminal_size)
        monkeypatch.setattr('click.formatting.FORCED_WIDTH', None)
        
        formatter = HelpFormatter(width=None, max_width=80)
        
        # width = max(min(40, 80) - 2, 50) = max(38, 50) = 50
        assert formatter.width == 50

    def test_init_width_calculation_with_large_terminal(self, monkeypatch):
        # Mock terminal size to be larger than max_width
        mock_terminal_size = Mock()
        mock_terminal_size.columns = 120
        monkeypatch.setattr(shutil, 'get_terminal_size', lambda: mock_terminal_size)
        monkeypatch.setattr('click.formatting.FORCED_WIDTH', None)
        
        formatter = HelpFormatter(width=None, max_width=80)
        
        # width = max(min(120, 80) - 2, 50) = max(78, 50) = 78
        assert formatter.width == 78
