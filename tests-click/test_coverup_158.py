# file: src/click/src/click/types.py:62-81
# asked: {"lines": [62, 72, 73, 76, 77, 79, 81], "branches": [[76, 77], [76, 79]]}
# gained: {"lines": [62, 72, 73, 76, 77, 79, 81], "branches": [[76, 77], [76, 79]]}

import pytest
import click.types as types

class CustomParamTypeNoName(types.ParamType):
    """Custom ParamType without a name attribute."""
    pass

class CustomParamTypeWithName(types.ParamType):
    """Custom ParamType with a name attribute."""
    name = "custom_type"

class CustomParamTypeEndingParamType(types.ParamType):
    """Custom ParamType with 'ParamType' in the class name."""
    name = "ending_param_type"

class CustomParamTypeEndingParameterType(types.ParamType):
    """Custom ParamType with 'ParameterType' in the class name."""
    name = "ending_parameter_type"

class CustomParamType(types.ParamType):
    """Custom ParamType with 'ParamType' suffix."""
    name = "custom"

def test_paramtype_to_info_dict_without_name():
    """Test ParamType.to_info_dict when the instance has no name attribute."""
    param_type = CustomParamTypeNoName()
    result = param_type.to_info_dict()
    
    assert result["param_type"] == "Custom"
    assert result["name"] == "Custom"

def test_paramtype_to_info_dict_with_name():
    """Test ParamType.to_info_dict when the instance has a name attribute."""
    param_type = CustomParamTypeWithName()
    result = param_type.to_info_dict()
    
    assert result["param_type"] == "Custom"
    assert result["name"] == "custom_type"

def test_paramtype_to_info_dict_removes_paramtype_suffix():
    """Test ParamType.to_info_dict removes 'ParamType' suffix from class name."""
    param_type = CustomParamTypeEndingParamType()
    result = param_type.to_info_dict()
    
    assert result["param_type"] == "Custom"
    assert result["name"] == "ending_param_type"

def test_paramtype_to_info_dict_removes_parametertype_suffix():
    """Test ParamType.to_info_dict removes 'ParameterType' suffix from class name."""
    param_type = CustomParamTypeEndingParameterType()
    result = param_type.to_info_dict()
    
    assert result["param_type"] == "Custom"
    assert result["name"] == "ending_parameter_type"

def test_paramtype_to_info_dict_standard_case():
    """Test ParamType.to_info_dict with standard ParamType suffix."""
    param_type = CustomParamType()
    result = param_type.to_info_dict()
    
    assert result["param_type"] == "Custom"
    assert result["name"] == "custom"
