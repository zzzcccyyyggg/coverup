# file: src/click/src/click/types.py:171-192
# asked: {"lines": [171, 172, 173, 174, 176, 177, 178, 179, 181, 184, 185, 186, 187, 188, 189, 190, 192], "branches": []}
# gained: {"lines": [171, 172, 173, 174, 176, 177, 178, 179, 181, 184, 185, 186, 187, 188, 189, 190, 192], "branches": []}

import pytest
import typing as t
from click.types import FuncParamType
from click.core import Context, Parameter
from click.exceptions import BadParameter


class TestFuncParamType:
    """Test cases for FuncParamType to achieve full coverage."""
    
    def test_func_param_type_init(self):
        """Test FuncParamType initialization."""
        def test_func(x):
            return x.upper()
        
        param_type = FuncParamType(test_func)
        assert param_type.name == "test_func"
        assert param_type.func is test_func
    
    def test_to_info_dict(self):
        """Test to_info_dict method."""
        def test_func(x):
            return x.upper()
        
        param_type = FuncParamType(test_func)
        info_dict = param_type.to_info_dict()
        assert "func" in info_dict
        assert info_dict["func"] is test_func
    
    def test_convert_success(self):
        """Test convert method with successful conversion."""
        def test_func(x):
            return int(x) * 2
        
        param_type = FuncParamType(test_func)
        result = param_type.convert("5", None, None)
        assert result == 10
    
    def test_convert_value_error_with_unicode_error(self):
        """Test convert method with ValueError that leads to UnicodeError."""
        def test_func(x):
            raise ValueError("test error")
        
        param_type = FuncParamType(test_func)
        
        # Create a value that will cause UnicodeError when converted to string
        class BadUnicodeValue:
            def __str__(self):
                raise UnicodeError("unicode error")
            
            def decode(self, encoding, errors):
                return "decoded_value"
        
        bad_value = BadUnicodeValue()
        
        with pytest.raises(BadParameter):
            param_type.convert(bad_value, None, None)
    
    def test_convert_value_error_with_string_conversion(self):
        """Test convert method with ValueError that can be converted to string."""
        def test_func(x):
            raise ValueError("test error")
        
        param_type = FuncParamType(test_func)
        
        # Create a value that can be converted to string
        class StringableValue:
            def __str__(self):
                return "string_value"
        
        stringable_value = StringableValue()
        
        with pytest.raises(BadParameter):
            param_type.convert(stringable_value, None, None)
    
    def test_convert_value_error_with_bytes(self):
        """Test convert method with ValueError and bytes value."""
        def test_func(x):
            raise ValueError("test error")
        
        param_type = FuncParamType(test_func)
        
        # Test with bytes that can be decoded
        bytes_value = b"test_bytes"
        
        with pytest.raises(BadParameter):
            param_type.convert(bytes_value, None, None)
