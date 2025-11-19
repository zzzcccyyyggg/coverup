# file: src/click/src/click/types.py:516-545
# asked: {"lines": [516, 519, 521, 522, 523, 524, 525, 526, 527, 529, 530, 531, 533, 534, 536, 537, 538, 539, 541, 542, 545], "branches": [[529, 530], [529, 536], [530, 531], [530, 533], [533, 534], [533, 536], [536, 537], [536, 545]]}
# gained: {"lines": [516, 519, 521, 522, 523, 524, 525, 526, 527, 529, 530, 531, 533, 534, 536, 537, 538, 539, 541, 542, 545], "branches": [[529, 530], [529, 536], [530, 531], [530, 533], [533, 534], [536, 537], [536, 545]]}

import pytest
import typing as t
from click.core import Context
from click.core import Parameter
from click.types import IntRange


class TestNumberRangeBase:
    """Test cases for _NumberRangeBase.convert method to cover lines 516-545."""
    
    def test_convert_with_clamp_min_open(self):
        """Test clamp behavior when value is below min with min_open=True."""
        # Create an IntRange with min=5, min_open=True, clamp=True
        number_range = IntRange(min=5, min_open=True, clamp=True)
        
        # Test conversion with clamping - value below min with open boundary
        result = number_range.convert("4", None, None)
        
        # Should clamp to min (5) but since min_open=True, it should clamp to next valid integer
        assert result == 6  # For integers with open boundary, clamp to next valid value
    
    def test_convert_with_clamp_max_open(self):
        """Test clamp behavior when value is above max with max_open=True."""
        # Create an IntRange with max=10, max_open=True, clamp=True
        number_range = IntRange(max=10, max_open=True, clamp=True)
        
        # Test conversion with clamping - value above max with open boundary
        result = number_range.convert("11", None, None)
        
        # Should clamp to max (10) but since max_open=True, it should clamp to previous valid integer
        assert result == 9  # For integers with open boundary, clamp to previous valid value
    
    def test_convert_with_clamp_both_bounds(self):
        """Test clamp behavior when value is outside both bounds."""
        # Create an IntRange with min=0, max=100, clamp=True
        number_range = IntRange(min=0, max=100, clamp=True)
        
        # Test conversion with clamping - should clamp to max
        result = number_range.convert("150", None, None)
        assert result == 100
    
    def test_convert_fail_below_min_open(self):
        """Test failure when value is below min with min_open=True and no clamping."""
        # Create an IntRange with min=5, min_open=True, clamp=False
        number_range = IntRange(min=5, min_open=True, clamp=False)
        
        # Should fail with range error when value is below min with open boundary
        with pytest.raises(Exception):  # Replace with specific exception type
            number_range.convert("4", None, None)
    
    def test_convert_fail_above_max_open(self):
        """Test failure when value is above max with max_open=True and no clamping."""
        # Create an IntRange with max=10, max_open=True, clamp=False
        number_range = IntRange(max=10, max_open=True, clamp=False)
        
        # Should fail with range error when value is above max with open boundary
        with pytest.raises(Exception):  # Replace with specific exception type
            number_range.convert("11", None, None)
    
    def test_convert_fail_both_outside_bounds(self):
        """Test failure when value is outside both bounds with no clamping."""
        # Create an IntRange with min=0, max=100, clamp=False
        number_range = IntRange(min=0, max=100, clamp=False)
        
        # Should fail with range error
        with pytest.raises(Exception):  # Replace with specific exception type
            number_range.convert("150", None, None)
    
    def test_convert_within_range_no_clamp(self):
        """Test successful conversion when value is within range and no clamping needed."""
        # Create an IntRange with min=0, max=100, clamp=False
        number_range = IntRange(min=0, max=100, clamp=False)
        
        # Should return the value unchanged
        result = number_range.convert("50", None, None)
        assert result == 50
    
    def test_convert_exactly_at_min_closed(self):
        """Test behavior when value is exactly at min with min_open=False."""
        # Create an IntRange with min=5, min_open=False, clamp=False
        number_range = IntRange(min=5, min_open=False, clamp=False)
        
        # Should succeed since min is inclusive
        result = number_range.convert("5", None, None)
        assert result == 5
    
    def test_convert_exactly_at_max_closed(self):
        """Test behavior when value is exactly at max with max_open=False."""
        # Create an IntRange with max=10, max_open=False, clamp=False
        number_range = IntRange(max=10, max_open=False, clamp=False)
        
        # Should succeed since max is inclusive
        result = number_range.convert("10", None, None)
        assert result == 10
    
    def test_convert_below_min_closed_no_clamp(self):
        """Test failure when value is below min with closed boundary and no clamping."""
        # Create an IntRange with min=5, min_open=False, clamp=False
        number_range = IntRange(min=5, min_open=False, clamp=False)
        
        # Should fail with range error
        with pytest.raises(Exception):  # Replace with specific exception type
            number_range.convert("4", None, None)
    
    def test_convert_above_max_closed_no_clamp(self):
        """Test failure when value is above max with closed boundary and no clamping."""
        # Create an IntRange with max=10, max_open=False, clamp=False
        number_range = IntRange(max=10, max_open=False, clamp=False)
        
        # Should fail with range error
        with pytest.raises(Exception):  # Replace with specific exception type
            number_range.convert("11", None, None)
