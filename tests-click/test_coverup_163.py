# file: src/click/src/click/core.py:2191-2217
# asked: {"lines": [2191, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2210, 2211, 2215, 2216], "branches": []}
# gained: {"lines": [2191, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2210, 2211, 2215, 2216], "branches": []}

import pytest
import typing as t
from click.core import Option
from click.types import ParamType
from click._utils import UNSET

class MockParamType(ParamType):
    """Mock ParamType for testing."""
    name = "mock_type"
    
    def to_info_dict(self) -> dict[str, t.Any]:
        return {"name": self.name, "is_composite": self.is_composite}

class TestParameterToInfoDict:
    """Test cases for Parameter.to_info_dict method."""
    
    def test_to_info_dict_with_default_unset(self):
        """Test to_info_dict when default is UNSET."""
        param = Option(
            param_decls=["--test"],
            type=MockParamType(),
            default=UNSET
        )
        
        result = param.to_info_dict()
        
        assert result["name"] == "test"
        assert result["param_type_name"] == "option"
        assert result["opts"] == ["--test"]
        assert result["secondary_opts"] == []
        assert result["type"] == {"name": "mock_type", "is_composite": False}
        assert result["required"] is False
        assert result["nargs"] == 1
        assert result["multiple"] is False
        assert result["default"] is None  # UNSET should become None
        assert result["envvar"] is None
    
    def test_to_info_dict_with_default_set(self):
        """Test to_info_dict when default is set to a value."""
        param = Option(
            param_decls=["--value"],
            type=MockParamType(),
            default="test_default"
        )
        
        result = param.to_info_dict()
        
        assert result["name"] == "value"
        assert result["param_type_name"] == "option"
        assert result["opts"] == ["--value"]
        assert result["secondary_opts"] == []
        assert result["type"] == {"name": "mock_type", "is_composite": False}
        assert result["required"] is False
        assert result["nargs"] == 1
        assert result["multiple"] is False
        assert result["default"] == "test_default"  # Should keep the actual default
        assert result["envvar"] is None
    
    def test_to_info_dict_with_envvar(self):
        """Test to_info_dict when envvar is set."""
        param = Option(
            param_decls=["--env"],
            type=MockParamType(),
            envvar="TEST_ENV_VAR"
        )
        
        result = param.to_info_dict()
        
        assert result["name"] == "env"
        assert result["param_type_name"] == "option"
        assert result["opts"] == ["--env"]
        assert result["secondary_opts"] == []
        assert result["type"] == {"name": "mock_type", "is_composite": False}
        assert result["required"] is False
        assert result["nargs"] == 1
        assert result["multiple"] is False
        assert result["default"] is None  # UNSET becomes None
        assert result["envvar"] == "TEST_ENV_VAR"
    
    def test_to_info_dict_with_required_true(self):
        """Test to_info_dict when required is True."""
        param = Option(
            param_decls=["--req"],
            type=MockParamType(),
            required=True
        )
        
        result = param.to_info_dict()
        
        assert result["name"] == "req"
        assert result["param_type_name"] == "option"
        assert result["opts"] == ["--req"]
        assert result["secondary_opts"] == []
        assert result["type"] == {"name": "mock_type", "is_composite": False}
        assert result["required"] is True
        assert result["nargs"] == 1
        assert result["multiple"] is False
        assert result["default"] is None  # UNSET becomes None
        assert result["envvar"] is None
    
    def test_to_info_dict_with_multiple_true(self):
        """Test to_info_dict when multiple is True."""
        param = Option(
            param_decls=["--multi"],
            type=MockParamType(),
            multiple=True
        )
        
        result = param.to_info_dict()
        
        assert result["name"] == "multi"
        assert result["param_type_name"] == "option"
        assert result["opts"] == ["--multi"]
        assert result["secondary_opts"] == []
        assert result["type"] == {"name": "mock_type", "is_composite": False}
        assert result["required"] is False
        assert result["nargs"] == 1
        assert result["multiple"] is True
        assert result["default"] is None  # UNSET becomes None
        assert result["envvar"] is None
    
    def test_to_info_dict_with_custom_nargs(self):
        """Test to_info_dict with custom nargs value."""
        param = Option(
            param_decls=["--nargs"],
            type=MockParamType(),
            nargs=2
        )
        
        result = param.to_info_dict()
        
        assert result["name"] == "nargs"
        assert result["param_type_name"] == "option"
        assert result["opts"] == ["--nargs"]
        assert result["secondary_opts"] == []
        assert result["type"] == {"name": "mock_type", "is_composite": False}
        assert result["required"] is False
        assert result["nargs"] == 2
        assert result["multiple"] is False
        assert result["default"] is None  # UNSET becomes None
        assert result["envvar"] is None
