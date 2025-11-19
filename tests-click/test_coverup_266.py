# file: src/click/src/click/types.py:571-573
# asked: {"lines": [571, 572, 573], "branches": []}
# gained: {"lines": [571, 572, 573], "branches": []}

import pytest
from click.types import _NumberRangeBase

class TestNumberRangeBaseRepr:
    """Test cases for _NumberRangeBase.__repr__ method to achieve full coverage."""
    
    def test_repr_with_clamp(self):
        """Test __repr__ when clamp is True."""
        # Create instance with clamp=True
        num_range = _NumberRangeBase(min=0, max=100, clamp=True)
        result = repr(num_range)
        
        # Verify the representation includes "clamped"
        assert "clamped" in result
        assert result.startswith("<")
        assert result.endswith(">")
        # Verify the range description is included
        assert "0<=x<=100" in result
    
    def test_repr_without_clamp(self):
        """Test __repr__ when clamp is False."""
        # Create instance with clamp=False (default)
        num_range = _NumberRangeBase(min=0, max=100, clamp=False)
        result = repr(num_range)
        
        # Verify the representation does NOT include "clamped"
        assert "clamped" not in result
        assert result.startswith("<")
        assert result.endswith(">")
        # Verify the range description is included
        assert "0<=x<=100" in result
    
    def test_repr_with_min_only_and_clamp(self):
        """Test __repr__ with only min bound and clamp."""
        num_range = _NumberRangeBase(min=10, clamp=True)
        result = repr(num_range)
        
        # Verify the representation includes "clamped" and min bound
        assert "clamped" in result
        assert "x>=10" in result
    
    def test_repr_with_max_only_and_clamp(self):
        """Test __repr__ with only max bound and clamp."""
        num_range = _NumberRangeBase(max=50, clamp=True)
        result = repr(num_range)
        
        # Verify the representation includes "clamped" and max bound
        assert "clamped" in result
        assert "x<=50" in result
    
    def test_repr_with_open_bounds_and_clamp(self):
        """Test __repr__ with open bounds and clamp."""
        num_range = _NumberRangeBase(min=5, max=95, min_open=True, max_open=True, clamp=True)
        result = repr(num_range)
        
        # Verify the representation includes "clamped" and open bounds
        assert "clamped" in result
        assert "5<x<95" in result
