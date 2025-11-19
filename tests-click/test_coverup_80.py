# file: src/click/src/click/types.py:557-569
# asked: {"lines": [557, 559, 560, 561, 563, 564, 565, 567, 568, 569], "branches": [[559, 560], [559, 563], [563, 564], [563, 567]]}
# gained: {"lines": [557, 559, 560, 561, 563, 564, 565, 567, 568, 569], "branches": [[559, 560], [559, 563], [563, 564], [563, 567]]}

import pytest
from click.types import _NumberRangeBase


class TestNumberRangeBaseDescribeRange:
    """Test cases for _NumberRangeBase._describe_range method."""
    
    def test_describe_range_min_only_with_open(self):
        """Test range description when only min is set with open boundary."""
        param = _NumberRangeBase(min=10, min_open=True)
        result = param._describe_range()
        assert result == "x>10"
    
    def test_describe_range_min_only_with_closed(self):
        """Test range description when only min is set with closed boundary."""
        param = _NumberRangeBase(min=10, min_open=False)
        result = param._describe_range()
        assert result == "x>=10"
    
    def test_describe_range_max_only_with_open(self):
        """Test range description when only max is set with open boundary."""
        param = _NumberRangeBase(max=100, max_open=True)
        result = param._describe_range()
        assert result == "x<100"
    
    def test_describe_range_max_only_with_closed(self):
        """Test range description when only max is set with closed boundary."""
        param = _NumberRangeBase(max=100, max_open=False)
        result = param._describe_range()
        assert result == "x<=100"
    
    def test_describe_range_both_bounds_all_open(self):
        """Test range description when both bounds are set with open boundaries."""
        param = _NumberRangeBase(min=10, max=100, min_open=True, max_open=True)
        result = param._describe_range()
        assert result == "10<x<100"
    
    def test_describe_range_both_bounds_all_closed(self):
        """Test range description when both bounds are set with closed boundaries."""
        param = _NumberRangeBase(min=10, max=100, min_open=False, max_open=False)
        result = param._describe_range()
        assert result == "10<=x<=100"
    
    def test_describe_range_both_bounds_mixed_open_closed(self):
        """Test range description when both bounds are set with mixed boundaries."""
        param = _NumberRangeBase(min=10, max=100, min_open=True, max_open=False)
        result = param._describe_range()
        assert result == "10<x<=100"
    
    def test_describe_range_both_bounds_mixed_closed_open(self):
        """Test range description when both bounds are set with mixed boundaries."""
        param = _NumberRangeBase(min=10, max=100, min_open=False, max_open=True)
        result = param._describe_range()
        assert result == "10<=x<100"
