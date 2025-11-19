# file: src/click/src/click/types.py:83-90
# asked: {"lines": [83, 86, 87, 89, 90], "branches": [[89, 0], [89, 90]]}
# gained: {"lines": [83, 86, 87, 89, 90], "branches": [[89, 0], [89, 90]]}

import pytest
from click.types import ParamType
from click.core import Context, Parameter

class TestParamType:
    """Test cases for ParamType class to achieve full coverage."""
    
    def test_param_type_call_with_none_value(self):
        """Test that __call__ returns None when value is None."""
        param_type = ParamType()
        result = param_type(None)
        assert result is None
    
    def test_param_type_call_with_value_calls_convert(self, monkeypatch):
        """Test that __call__ calls convert method when value is not None."""
        param_type = ParamType()
        mock_convert = lambda self, value, param, ctx: "converted_value"
        monkeypatch.setattr(ParamType, "convert", mock_convert)
        
        result = param_type("test_value", param="test_param", ctx="test_ctx")
        assert result == "converted_value"
    
    def test_param_type_call_with_value_and_none_params(self, monkeypatch):
        """Test that __call__ calls convert method when value is not None and params are None."""
        param_type = ParamType()
        mock_convert = lambda self, value, param, ctx: "converted_value"
        monkeypatch.setattr(ParamType, "convert", mock_convert)
        
        result = param_type("test_value", param=None, ctx=None)
        assert result == "converted_value"
