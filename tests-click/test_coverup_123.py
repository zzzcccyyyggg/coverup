# file: src/click/src/click/types.py:491-503
# asked: {"lines": [491, 493, 494, 495, 496, 497, 499, 500, 501, 502, 503], "branches": []}
# gained: {"lines": [491, 493, 494, 495, 496, 497, 499, 500, 501, 502, 503], "branches": []}

import pytest
import click
from click.types import _NumberRangeBase


class TestNumberRangeBase:
    """Test cases for _NumberRangeBase class initialization and coverage."""
    
    def test_init_with_all_parameters(self):
        """Test _NumberRangeBase initialization with all parameters set."""
        # Test with all parameters explicitly set
        instance = _NumberRangeBase(
            min=10.5,
            max=100.0,
            min_open=True,
            max_open=True,
            clamp=True
        )
        
        # Verify all attributes are set correctly
        assert instance.min == 10.5
        assert instance.max == 100.0
        assert instance.min_open is True
        assert instance.max_open is True
        assert instance.clamp is True
    
    def test_init_with_min_only(self):
        """Test _NumberRangeBase initialization with only min parameter."""
        instance = _NumberRangeBase(min=5.0)
        
        assert instance.min == 5.0
        assert instance.max is None
        assert instance.min_open is False
        assert instance.max_open is False
        assert instance.clamp is False
    
    def test_init_with_max_only(self):
        """Test _NumberRangeBase initialization with only max parameter."""
        instance = _NumberRangeBase(max=50.0)
        
        assert instance.min is None
        assert instance.max == 50.0
        assert instance.min_open is False
        assert instance.max_open is False
        assert instance.clamp is False
    
    def test_init_with_min_open_only(self):
        """Test _NumberRangeBase initialization with only min_open parameter."""
        instance = _NumberRangeBase(min_open=True)
        
        assert instance.min is None
        assert instance.max is None
        assert instance.min_open is True
        assert instance.max_open is False
        assert instance.clamp is False
    
    def test_init_with_max_open_only(self):
        """Test _NumberRangeBase initialization with only max_open parameter."""
        instance = _NumberRangeBase(max_open=True)
        
        assert instance.min is None
        assert instance.max is None
        assert instance.min_open is False
        assert instance.max_open is True
        assert instance.clamp is False
    
    def test_init_with_clamp_only(self):
        """Test _NumberRangeBase initialization with only clamp parameter."""
        instance = _NumberRangeBase(clamp=True)
        
        assert instance.min is None
        assert instance.max is None
        assert instance.min_open is False
        assert instance.max_open is False
        assert instance.clamp is True
    
    def test_init_with_no_parameters(self):
        """Test _NumberRangeBase initialization with no parameters (default values)."""
        instance = _NumberRangeBase()
        
        assert instance.min is None
        assert instance.max is None
        assert instance.min_open is False
        assert instance.max_open is False
        assert instance.clamp is False
    
    def test_init_with_combination_parameters(self):
        """Test _NumberRangeBase initialization with various parameter combinations."""
        # Test min and max with clamp
        instance1 = _NumberRangeBase(min=1.0, max=10.0, clamp=True)
        assert instance1.min == 1.0
        assert instance1.max == 10.0
        assert instance1.clamp is True
        
        # Test min_open and max_open together
        instance2 = _NumberRangeBase(min_open=True, max_open=True)
        assert instance2.min_open is True
        assert instance2.max_open is True
        
        # Test min with min_open
        instance3 = _NumberRangeBase(min=5.0, min_open=True)
        assert instance3.min == 5.0
        assert instance3.min_open is True
        
        # Test max with max_open
        instance4 = _NumberRangeBase(max=100.0, max_open=True)
        assert instance4.max == 100.0
        assert instance4.max_open is True
