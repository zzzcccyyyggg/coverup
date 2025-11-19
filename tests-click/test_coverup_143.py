# file: src/click/src/click/types.py:505-514
# asked: {"lines": [505, 506, 507, 508, 509, 510, 511, 512, 514], "branches": []}
# gained: {"lines": [505, 506, 507, 508, 509, 510, 511, 512, 514], "branches": []}

import pytest
import click.types


class TestNumberRangeBase:
    def test_to_info_dict_returns_all_attributes(self):
        """Test that to_info_dict returns all attributes including min, max, min_open, max_open, and clamp."""
        # Create a _NumberRangeBase instance with specific values
        number_range = click.types._NumberRangeBase(
            min=0.0,
            max=100.0,
            min_open=True,
            max_open=False,
            clamp=True
        )
        
        # Call to_info_dict method
        info_dict = number_range.to_info_dict()
        
        # Verify all attributes are present in the returned dictionary
        assert info_dict['min'] == 0.0
        assert info_dict['max'] == 100.0
        assert info_dict['min_open'] is True
        assert info_dict['max_open'] is False
        assert info_dict['clamp'] is True
        
        # Verify the dictionary contains the expected keys
        expected_keys = {'min', 'max', 'min_open', 'max_open', 'clamp'}
        assert expected_keys.issubset(info_dict.keys())

    def test_to_info_dict_with_none_bounds(self):
        """Test to_info_dict with None min and max values."""
        # Create a _NumberRangeBase instance with None bounds
        number_range = click.types._NumberRangeBase(
            min=None,
            max=None,
            min_open=False,
            max_open=True,
            clamp=False
        )
        
        # Call to_info_dict method
        info_dict = number_range.to_info_dict()
        
        # Verify all attributes are present in the returned dictionary
        assert info_dict['min'] is None
        assert info_dict['max'] is None
        assert info_dict['min_open'] is False
        assert info_dict['max_open'] is True
        assert info_dict['clamp'] is False

    def test_to_info_dict_inherits_parent_info(self):
        """Test that to_info_dict includes information from parent class."""
        # Create a _NumberRangeBase instance
        number_range = click.types._NumberRangeBase(
            min=10.0,
            max=20.0,
            min_open=False,
            max_open=False,
            clamp=True
        )
        
        # Call to_info_dict method
        info_dict = number_range.to_info_dict()
        
        # Verify the dictionary contains at least the expected keys
        # (parent class may add additional keys)
        expected_keys = {'min', 'max', 'min_open', 'max_open', 'clamp'}
        assert expected_keys.issubset(info_dict.keys())
