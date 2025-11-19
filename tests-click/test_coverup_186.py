# file: src/click/src/click/types.py:697-710
# asked: {"lines": [697, 698, 708, 709, 710], "branches": [[708, 709], [708, 710]]}
# gained: {"lines": [697, 698, 708, 709, 710], "branches": [[708, 709], [708, 710]]}

import pytest
from click.types import BoolParamType


class TestBoolParamTypeStrToBool:
    """Test cases for BoolParamType.str_to_bool method to achieve full coverage."""
    
    def test_str_to_bool_with_bool_true(self):
        """Test that boolean True is returned as-is."""
        result = BoolParamType.str_to_bool(True)
        assert result is True
    
    def test_str_to_bool_with_bool_false(self):
        """Test that boolean False is returned as-is."""
        result = BoolParamType.str_to_bool(False)
        assert result is False
    
    def test_str_to_bool_with_valid_string_true(self):
        """Test that valid true string returns True."""
        result = BoolParamType.str_to_bool('true')
        assert result is True
    
    def test_str_to_bool_with_valid_string_false(self):
        """Test that valid false string returns False."""
        result = BoolParamType.str_to_bool('false')
        assert result is False
    
    def test_str_to_bool_with_whitespace_string(self):
        """Test that string with whitespace is properly stripped."""
        result = BoolParamType.str_to_bool('  true  ')
        assert result is True
    
    def test_str_to_bool_with_mixed_case_string(self):
        """Test that mixed case string is properly lowercased."""
        result = BoolParamType.str_to_bool('TrUe')
        assert result is True
    
    def test_str_to_bool_with_unknown_string(self):
        """Test that unknown string returns None."""
        result = BoolParamType.str_to_bool('unknown')
        assert result is None
    
    def test_str_to_bool_with_empty_string(self):
        """Test that empty string returns False (as per bool_states mapping)."""
        result = BoolParamType.str_to_bool('')
        assert result is False
    
    def test_str_to_bool_with_numeric_strings(self):
        """Test that numeric strings '1' and '0' work correctly."""
        assert BoolParamType.str_to_bool('1') is True
        assert BoolParamType.str_to_bool('0') is False
    
    def test_str_to_bool_with_abbreviated_strings(self):
        """Test that abbreviated strings like 't', 'f', 'y', 'n' work correctly."""
        assert BoolParamType.str_to_bool('t') is True
        assert BoolParamType.str_to_bool('f') is False
        assert BoolParamType.str_to_bool('y') is True
        assert BoolParamType.str_to_bool('n') is False
    
    def test_str_to_bool_with_on_off_strings(self):
        """Test that 'on' and 'off' strings work correctly."""
        assert BoolParamType.str_to_bool('on') is True
        assert BoolParamType.str_to_bool('off') is False
    
    def test_str_to_bool_with_yes_no_strings(self):
        """Test that 'yes' and 'no' strings work correctly."""
        assert BoolParamType.str_to_bool('yes') is True
        assert BoolParamType.str_to_bool('no') is False
