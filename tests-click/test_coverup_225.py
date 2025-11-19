# file: src/click/src/click/core.py:3298-3313
# asked: {"lines": [3298, 3304, 3305, 3307, 3308, 3310, 3313], "branches": [[3304, 3305], [3304, 3313], [3307, 3308], [3307, 3310]]}
# gained: {"lines": [3298, 3304, 3305, 3307, 3308, 3310, 3313], "branches": [[3304, 3305], [3304, 3313], [3307, 3308], [3307, 3310]]}

import pytest
import click
from click.core import Option, Context
from click._utils import UNSET
from click.exceptions import MissingParameter


class TestOptionProcessValue:
    """Test cases for Option.process_value method to achieve full coverage."""
    
    def test_process_value_flag_bool_unset_no_callback(self):
        """Test process_value when is_flag=True, required=False, is_bool_flag=True, value=UNSET, and no callback."""
        ctx = Context(click.Command('test'))
        option = Option(['--flag'], is_flag=True, required=False)
        
        # Verify the option has the expected properties
        assert option.is_flag is True
        assert option.required is False
        assert option.is_bool_flag is True
        
        result = option.process_value(ctx, UNSET)
        assert result is False
    
    def test_process_value_flag_bool_unset_with_callback(self):
        """Test process_value when is_flag=True, required=False, is_bool_flag=True, value=UNSET, and with callback."""
        ctx = Context(click.Command('test'))
        
        def mock_callback(ctx, param, value):
            return "callback_result"
        
        option = Option(['--flag'], is_flag=True, required=False, callback=mock_callback)
        
        # Verify the option has the expected properties
        assert option.is_flag is True
        assert option.required is False
        assert option.is_bool_flag is True
        assert option.callback is not None
        
        result = option.process_value(ctx, UNSET)
        assert result == "callback_result"
    
    def test_process_value_non_flag_case(self):
        """Test process_value when is_flag=False, which should call super().process_value."""
        ctx = Context(click.Command('test'))
        option = Option(['--value'], is_flag=False, required=False)
        
        # Verify the option has the expected properties
        assert option.is_flag is False
        
        # Test with a regular value to ensure super().process_value is called
        result = option.process_value(ctx, "test_value")
        # The parent process_value should handle type conversion and return the value
        assert result == "test_value"
    
    def test_process_value_flag_but_not_bool(self):
        """Test process_value when is_flag=True but not a boolean flag."""
        ctx = Context(click.Command('test'))
        option = Option(['--flag'], is_flag=True, flag_value="custom_value")
        
        # Verify the option has the expected properties
        assert option.is_flag is True
        assert option.is_bool_flag is False  # Not a boolean flag due to custom flag_value
        
        # Test with UNSET value - should call super().process_value
        result = option.process_value(ctx, UNSET)
        # For non-bool flags with UNSET, parent should return UNSET
        assert result is UNSET
    
    def test_process_value_flag_required(self):
        """Test process_value when is_flag=True but required=True."""
        ctx = Context(click.Command('test'))
        option = Option(['--flag'], is_flag=True, required=True)
        
        # Verify the option has the expected properties
        assert option.is_flag is True
        assert option.required is True
        assert option.is_bool_flag is True
        
        # Test with UNSET value - should call super().process_value which raises MissingParameter
        with pytest.raises(MissingParameter, match="Missing parameter: flag"):
            option.process_value(ctx, UNSET)
    
    def test_process_value_flag_with_value_not_unset(self):
        """Test process_value when is_flag=True but value is not UNSET."""
        ctx = Context(click.Command('test'))
        option = Option(['--flag'], is_flag=True, required=False)
        
        # Verify the option has the expected properties
        assert option.is_flag is True
        assert option.required is False
        assert option.is_bool_flag is True
        
        # Test with a valid boolean value - should call super().process_value
        result = option.process_value(ctx, True)
        # Parent should handle valid boolean values
        assert result is True
    
    def test_process_value_flag_with_valid_string_bool(self):
        """Test process_value when is_flag=True with a valid string boolean value."""
        ctx = Context(click.Command('test'))
        option = Option(['--flag'], is_flag=True, required=False)
        
        # Verify the option has the expected properties
        assert option.is_flag is True
        assert option.required is False
        assert option.is_bool_flag is True
        
        # Test with a valid string boolean value
        result = option.process_value(ctx, "true")
        # Parent should convert valid string boolean to True
        assert result is True
