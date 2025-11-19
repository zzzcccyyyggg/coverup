# file: src/click/src/click/_termui_impl.py:209-234
# asked: {"lines": [209, 210, 212, 213, 214, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 227, 228, 229, 230, 231, 232, 234], "branches": [[213, 214], [213, 216], [216, 217], [216, 218], [218, 219], [218, 220], [220, 221], [220, 222], [222, 223], [222, 227], [224, 225], [224, 227]]}
# gained: {"lines": [209, 210, 212, 213, 214, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 227, 228, 229, 230, 231, 232, 234], "branches": [[213, 214], [213, 216], [216, 217], [216, 218], [218, 219], [218, 220], [220, 221], [220, 222], [222, 223], [222, 227], [224, 225], [224, 227]]}

import pytest
from click._termui_impl import ProgressBar
from unittest.mock import Mock, patch


class TestProgressBarFormatProgressLine:
    def test_format_progress_line_with_show_pos_and_show_percent(self):
        """Test format_progress_line when show_pos and show_percent are True"""
        bar = ProgressBar(range(10), length=10, show_pos=True, show_percent=True)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        # Check that the result is properly formatted
        assert isinstance(result, str)
        assert result.rstrip() == result  # Should be rstrip()'d
        # The bar template might just show the bar itself without info
        assert len(result) > 0

    def test_format_progress_line_with_show_eta_and_eta_known(self):
        """Test format_progress_line when show_eta is True and eta_known is True"""
        bar = ProgressBar(range(10), length=10, show_eta=True)
        bar.pos = 5
        bar.eta_known = True
        bar.finished = False
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_item_show_func(self):
        """Test format_progress_line when item_show_func is provided and returns non-None"""
        def item_show_func(item):
            return f"Item: {item}"
        
        bar = ProgressBar(range(10), length=10, item_show_func=item_show_func)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_item_show_func_returning_none(self):
        """Test format_progress_line when item_show_func returns None"""
        def item_show_func(item):
            return None
        
        bar = ProgressBar(range(10), length=10, item_show_func=item_show_func)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_length_and_show_percent_none(self):
        """Test format_progress_line when length is set and show_percent is None"""
        bar = ProgressBar(range(10), length=10, show_percent=None, show_pos=False)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_length_and_show_percent_none_and_show_pos_true(self):
        """Test format_progress_line when length is set, show_percent is None, and show_pos is True"""
        bar = ProgressBar(range(10), length=10, show_percent=None, show_pos=True)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_finished_and_show_eta(self):
        """Test format_progress_line when finished is True and show_eta is True"""
        bar = ProgressBar(range(10), length=10, show_eta=True)
        bar.pos = 10
        bar.eta_known = True
        bar.finished = True
        bar.current_item = 10
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_eta_unknown_and_show_eta(self):
        """Test format_progress_line when show_eta is True but eta_known is False"""
        bar = ProgressBar(range(10), length=10, show_eta=True)
        bar.pos = 5
        bar.eta_known = False
        bar.finished = False
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_complex_case_all_features(self):
        """Test format_progress_line with all features enabled"""
        def item_show_func(item):
            return f"Processing: {item}"
        
        bar = ProgressBar(
            range(100), 
            length=100, 
            show_pos=True, 
            show_percent=True, 
            show_eta=True,
            item_show_func=item_show_func,
            label="Test Progress"
        )
        bar.pos = 50
        bar.eta_known = True
        bar.finished = False
        bar.current_item = 50
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_custom_bar_template(self):
        """Test format_progress_line with a custom bar template that includes info"""
        custom_template = "%(label)s [%(bar)s] %(info)s"
        bar = ProgressBar(range(10), length=10, bar_template=custom_template, show_pos=True, show_percent=True)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_no_info_bits(self):
        """Test format_progress_line when no info bits are added"""
        bar = ProgressBar(range(10), length=10, show_pos=False, show_percent=False, show_eta=False)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_empty_label(self):
        """Test format_progress_line with empty label"""
        bar = ProgressBar(range(10), length=10, label="", show_pos=True, show_percent=True)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_with_none_length(self):
        """Test format_progress_line when length is None"""
        bar = ProgressBar(range(10), length=None, show_pos=True, show_percent=True)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)
        assert result.rstrip() == result

    def test_format_progress_line_returns_string(self):
        """Test that format_progress_line always returns a string"""
        bar = ProgressBar(range(10), length=10)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        assert isinstance(result, str)

    def test_format_progress_line_rstrip_behavior(self):
        """Test that format_progress_line properly strips trailing whitespace"""
        bar = ProgressBar(range(10), length=10)
        bar.pos = 5
        bar.current_item = 5
        
        result = bar.format_progress_line()
        
        # The result should have no trailing whitespace
        assert result == result.rstrip()
