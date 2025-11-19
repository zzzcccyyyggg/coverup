# file: src/click/src/click/types.py:102-124
# asked: {"lines": [102, 124], "branches": []}
# gained: {"lines": [102, 124], "branches": []}

import pytest
import typing as t
from click.core import Context
from click.core import Parameter
from click.types import ParamType
from click.core import Command


class TestParamTypeConvert:
    """Test cases for ParamType.convert method to achieve full coverage."""
    
    def test_convert_with_none_context_and_param(self):
        """Test convert method when both context and parameter are None."""
        param_type = ParamType()
        value = "test_value"
        
        result = param_type.convert(value, None, None)
        
        assert result == value
    
    def test_convert_with_context_only(self):
        """Test convert method when only context is provided."""
        param_type = ParamType()
        value = "test_value"
        command = Command("test_command")
        ctx = Context(command)
        
        result = param_type.convert(value, None, ctx)
        
        assert result == value
    
    def test_convert_with_param_only(self):
        """Test convert method when only parameter is provided."""
        param_type = ParamType()
        value = "test_value"
        
        # Create a mock parameter object with minimal required attributes
        class MockParameter:
            def __init__(self):
                self.name = "test_param"
        
        param = MockParameter()
        
        result = param_type.convert(value, param, None)
        
        assert result == value
    
    def test_convert_with_both_context_and_param(self):
        """Test convert method when both context and parameter are provided."""
        param_type = ParamType()
        value = "test_value"
        command = Command("test_command")
        ctx = Context(command)
        
        # Create a mock parameter object with minimal required attributes
        class MockParameter:
            def __init__(self):
                self.name = "test_param"
        
        param = MockParameter()
        
        result = param_type.convert(value, param, ctx)
        
        assert result == value
    
    def test_convert_with_different_value_types(self):
        """Test convert method with various value types."""
        param_type = ParamType()
        
        # Test with string
        result1 = param_type.convert("string_value", None, None)
        assert result1 == "string_value"
        
        # Test with integer
        result2 = param_type.convert(42, None, None)
        assert result2 == 42
        
        # Test with list
        result3 = param_type.convert([1, 2, 3], None, None)
        assert result3 == [1, 2, 3]
        
        # Test with dict
        result4 = param_type.convert({"key": "value"}, None, None)
        assert result4 == {"key": "value"}
