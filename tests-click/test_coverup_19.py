# file: src/click/src/click/types.py:1112-1169
# asked: {"lines": [1112, 1117, 1119, 1120, 1123, 1124, 1129, 1130, 1132, 1134, 1136, 1138, 1139, 1141, 1142, 1144, 1145, 1147, 1148, 1150, 1151, 1153, 1154, 1156, 1157, 1159, 1160, 1161, 1162, 1163, 1165, 1167, 1169], "branches": [[1119, 1120], [1119, 1138], [1120, 1123], [1120, 1134], [1123, 1124], [1123, 1136], [1129, 1130], [1129, 1132], [1138, 1139], [1138, 1141], [1141, 1142], [1141, 1144], [1144, 1145], [1144, 1147], [1147, 1148], [1147, 1150], [1150, 1151], [1150, 1153], [1153, 1154], [1153, 1156], [1156, 1157], [1156, 1159], [1159, 1160], [1161, 1162], [1161, 1169]]}
# gained: {"lines": [1112, 1117, 1119, 1120, 1123, 1124, 1129, 1130, 1132, 1134, 1136, 1138, 1139, 1141, 1142, 1144, 1145, 1147, 1148, 1150, 1151, 1153, 1154, 1156, 1157, 1159, 1160, 1161, 1162, 1163, 1165, 1167, 1169], "branches": [[1119, 1120], [1119, 1138], [1120, 1123], [1120, 1134], [1123, 1124], [1123, 1136], [1129, 1130], [1129, 1132], [1138, 1139], [1138, 1141], [1141, 1142], [1141, 1144], [1144, 1145], [1144, 1147], [1147, 1148], [1147, 1150], [1150, 1151], [1150, 1153], [1153, 1154], [1153, 1156], [1156, 1157], [1156, 1159], [1159, 1160], [1161, 1162]]}

import pytest
import typing as t
from click.types import convert_type, ParamType, Tuple, FuncParamType, STRING, INT, FLOAT, BOOL


class CustomParamType(ParamType):
    """A custom parameter type for testing."""
    name = "custom"

    def convert(self, value, param=None, ctx=None):
        return value


def test_convert_type_with_tuple_default():
    """Test convert_type with tuple default value."""
    # Test with non-empty tuple default containing tuples (nested structure)
    result = convert_type(None, default=((1, 2), (3, 4)))
    assert isinstance(result, Tuple)
    
    # Test with empty tuple default
    result = convert_type(None, default=())
    assert result is STRING
    
    # Test with list default containing lists (nested structure)
    result = convert_type(None, default=[[1, 2], [3, 4]])
    assert isinstance(result, Tuple)


def test_convert_type_with_nested_tuple_default():
    """Test convert_type with nested tuple/list default value."""
    # Test with tuple of tuples
    result = convert_type(None, default=((1, 2), (3, 4)))
    assert isinstance(result, Tuple)
    
    # Test with list of lists
    result = convert_type(None, default=[[1, 2], [3, 4]])
    assert isinstance(result, Tuple)


def test_convert_type_with_tuple_type():
    """Test convert_type with tuple type parameter."""
    result = convert_type((str, int))
    assert isinstance(result, Tuple)


def test_convert_type_with_param_type_instance():
    """Test convert_type with ParamType instance."""
    custom_type = CustomParamType()
    result = convert_type(custom_type)
    assert result is custom_type


def test_convert_type_with_basic_types():
    """Test convert_type with basic Python types."""
    assert convert_type(str) is STRING
    assert convert_type(int) is INT
    assert convert_type(float) is FLOAT
    assert convert_type(bool) is BOOL


def test_convert_type_with_none_and_guessed_type():
    """Test convert_type with None type and guessed type."""
    # When type is None and default is provided, should guess type
    result = convert_type(None, default="test")
    assert result is STRING
    
    # When type is explicitly None
    result = convert_type(None)
    assert result is STRING


def test_convert_type_with_uninstantiated_param_type_subclass():
    """Test convert_type with uninstantiated ParamType subclass."""
    with pytest.raises(AssertionError) as exc_info:
        convert_type(CustomParamType)
    assert "uninstantiated parameter type" in str(exc_info.value)


def test_convert_type_with_func_param_type():
    """Test convert_type with function type."""
    def custom_func(x):
        return x
    
    result = convert_type(custom_func)
    assert isinstance(result, FuncParamType)
    assert result.func is custom_func


def test_convert_type_with_guessed_type_fallback():
    """Test convert_type fallback to STRING when type is guessed but not basic."""
    class CustomClass:
        pass
    
    # When type is guessed from default but not a basic type
    result = convert_type(None, default=CustomClass())
    assert result is STRING


def test_convert_type_with_simple_tuple_default():
    """Test convert_type with simple tuple default (non-nested)."""
    # For a simple tuple like (1, 2, 3), the type is inferred as int
    # and since int is a basic type, it should return INT
    result = convert_type(None, default=(1, 2, 3))
    assert result is INT
    
    # Same for list
    result = convert_type(None, default=[1, 2, 3])
    assert result is INT


def test_convert_type_with_simple_tuple_default_string():
    """Test convert_type with simple tuple default containing strings."""
    # For a tuple of strings, should return STRING
    result = convert_type(None, default=("a", "b", "c"))
    assert result is STRING


def test_convert_type_with_simple_tuple_default_float():
    """Test convert_type with simple tuple default containing floats."""
    # For a tuple of floats, should return FLOAT
    result = convert_type(None, default=(1.1, 2.2, 3.3))
    assert result is FLOAT


def test_convert_type_with_simple_tuple_default_bool():
    """Test convert_type with simple tuple default containing booleans."""
    # For a tuple of booleans, should return BOOL
    result = convert_type(None, default=(True, False, True))
    assert result is BOOL
