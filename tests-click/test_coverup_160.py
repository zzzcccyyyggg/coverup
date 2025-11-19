# file: src/click/src/click/core.py:2393-2409
# asked: {"lines": [2393, 2403, 2404, 2406, 2407, 2409], "branches": [[2403, 2404], [2403, 2406], [2406, 2407], [2406, 2409]]}
# gained: {"lines": [2393, 2403, 2404, 2406, 2407, 2409], "branches": [[2403, 2404], [2403, 2406], [2406, 2407], [2406, 2409]]}

import pytest
from click.core import Option, Argument
from click._utils import UNSET


class TestParameterValueIsMissing:
    """Test cases for Parameter.value_is_missing method to achieve full coverage."""
    
    def test_value_is_missing_with_unset(self):
        """Test that UNSET value returns True."""
        param = Option(['--test'])
        assert param.value_is_missing(UNSET) is True
    
    def test_value_is_missing_with_empty_tuple_nargs_not_1(self):
        """Test that empty tuple returns True when nargs != 1."""
        param = Option(['--test'], nargs=2)
        assert param.value_is_missing(()) is True
    
    def test_value_is_missing_with_empty_tuple_multiple_true(self):
        """Test that empty tuple returns True when multiple is True."""
        param = Option(['--test'], multiple=True)
        assert param.value_is_missing(()) is True
    
    def test_value_is_missing_with_empty_tuple_nargs_not_1_and_multiple(self):
        """Test that empty tuple returns True when both nargs != 1 and multiple is True."""
        param = Option(['--test'], nargs=2, multiple=True)
        assert param.value_is_missing(()) is True
    
    def test_value_is_missing_with_non_empty_tuple_nargs_not_1(self):
        """Test that non-empty tuple returns False when nargs != 1."""
        param = Option(['--test'], nargs=2)
        assert param.value_is_missing(("value1", "value2")) is False
    
    def test_value_is_missing_with_empty_tuple_nargs_1_and_multiple_false(self):
        """Test that empty tuple returns False when nargs=1 and multiple=False."""
        param = Option(['--test'], nargs=1, multiple=False)
        assert param.value_is_missing(()) is False
    
    def test_value_is_missing_with_non_unset_value(self):
        """Test that non-UNSET, non-tuple value returns False."""
        param = Option(['--test'])
        assert param.value_is_missing("some_value") is False
    
    def test_value_is_missing_with_none_value(self):
        """Test that None value returns False."""
        param = Option(['--test'])
        assert param.value_is_missing(None) is False
    
    def test_value_is_missing_with_false_value(self):
        """Test that False value returns False."""
        param = Option(['--test'])
        assert param.value_is_missing(False) is False
    
    def test_value_is_missing_with_zero_value(self):
        """Test that 0 value returns False."""
        param = Option(['--test'])
        assert param.value_is_missing(0) is False
    
    def test_value_is_missing_with_argument_unset(self):
        """Test that UNSET value returns True for Argument."""
        param = Argument(['test'])
        assert param.value_is_missing(UNSET) is True
    
    def test_value_is_missing_with_argument_empty_tuple_nargs_not_1(self):
        """Test that empty tuple returns True when nargs != 1 for Argument."""
        param = Argument(['test'], nargs=2)
        assert param.value_is_missing(()) is True
