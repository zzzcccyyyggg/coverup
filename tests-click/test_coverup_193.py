# file: src/click/src/click/_utils.py:7-19
# asked: {"lines": [7, 8, 15, 16, 18, 19], "branches": []}
# gained: {"lines": [7, 8, 15, 16, 18, 19], "branches": []}

import pytest
from click._utils import Sentinel

class TestSentinel:
    def test_sentinel_enum_members_exist(self):
        """Test that Sentinel enum has expected members."""
        assert hasattr(Sentinel, 'UNSET')
        assert hasattr(Sentinel, 'FLAG_NEEDS_VALUE')
        assert isinstance(Sentinel.UNSET, Sentinel)
        assert isinstance(Sentinel.FLAG_NEEDS_VALUE, Sentinel)
    
    def test_sentinel_repr_method(self):
        """Test the __repr__ method of Sentinel enum members."""
        assert repr(Sentinel.UNSET) == "Sentinel.UNSET"
        assert repr(Sentinel.FLAG_NEEDS_VALUE) == "Sentinel.FLAG_NEEDS_VALUE"
    
    def test_sentinel_members_are_distinct_objects(self):
        """Test that different Sentinel members are distinct objects."""
        assert Sentinel.UNSET is not Sentinel.FLAG_NEEDS_VALUE
        assert Sentinel.UNSET.value is not Sentinel.FLAG_NEEDS_VALUE.value
