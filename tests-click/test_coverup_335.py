# file: src/click/src/click/types.py:126-134
# asked: {"lines": [126, 134], "branches": []}
# gained: {"lines": [126, 134], "branches": []}

import pytest
from click.types import ParamType

class TestParamTypeSplitEnvvarValue:
    """Test cases for ParamType.split_envvar_value method."""
    
    def test_split_envvar_value_with_none_splitter_and_empty_string(self):
        """Test split_envvar_value with None envvar_list_splitter and empty string."""
        param_type = ParamType()
        param_type.envvar_list_splitter = None
        
        result = param_type.split_envvar_value("")
        assert result == []
    
    def test_split_envvar_value_with_none_splitter_and_whitespace(self):
        """Test split_envvar_value with None envvar_list_splitter and whitespace string."""
        param_type = ParamType()
        param_type.envvar_list_splitter = None
        
        result = param_type.split_envvar_value("   ")
        assert result == []
    
    def test_split_envvar_value_with_none_splitter_and_whitespace_around_values(self):
        """Test split_envvar_value with None envvar_list_splitter and values with surrounding whitespace."""
        param_type = ParamType()
        param_type.envvar_list_splitter = None
        
        result = param_type.split_envvar_value("  value1 value2  ")
        assert result == ["value1", "value2"]
    
    def test_split_envvar_value_with_custom_splitter_and_empty_string(self):
        """Test split_envvar_value with custom envvar_list_splitter and empty string."""
        param_type = ParamType()
        param_type.envvar_list_splitter = ","
        
        result = param_type.split_envvar_value("")
        assert result == [""]
    
    def test_split_envvar_value_with_custom_splitter_and_leading_trailing_delimiters(self):
        """Test split_envvar_value with custom envvar_list_splitter and leading/trailing delimiters."""
        param_type = ParamType()
        param_type.envvar_list_splitter = ","
        
        result = param_type.split_envvar_value(",value1,value2,")
        assert result == ["", "value1", "value2", ""]
    
    def test_split_envvar_value_with_custom_splitter_and_no_delimiters(self):
        """Test split_envvar_value with custom envvar_list_splitter and no delimiters."""
        param_type = ParamType()
        param_type.envvar_list_splitter = ","
        
        result = param_type.split_envvar_value("value1 value2")
        assert result == ["value1 value2"]
    
    def test_split_envvar_value_with_custom_splitter_and_multiple_delimiters(self):
        """Test split_envvar_value with custom envvar_list_splitter and multiple consecutive delimiters."""
        param_type = ParamType()
        param_type.envvar_list_splitter = ","
        
        result = param_type.split_envvar_value("value1,,value2")
        assert result == ["value1", "", "value2"]
