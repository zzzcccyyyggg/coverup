# file: src/click/src/click/types.py:195-204
# asked: {"lines": [195, 196, 198, 201, 203, 204], "branches": []}
# gained: {"lines": [195, 196, 198, 201, 203, 204], "branches": []}

import pytest
from click.types import UnprocessedParamType
from click.core import Context, Option, Command


class TestUnprocessedParamType:
    """Test cases for UnprocessedParamType to achieve full coverage."""
    
    def test_convert_returns_value_unchanged(self):
        """Test that convert method returns the value unchanged."""
        param_type = UnprocessedParamType()
        test_value = "test_string"
        result = param_type.convert(test_value, None, None)
        assert result == test_value
        
        # Test with different types
        assert param_type.convert(123, None, None) == 123
        assert param_type.convert([1, 2, 3], None, None) == [1, 2, 3]
        assert param_type.convert({"key": "value"}, None, None) == {"key": "value"}
        assert param_type.convert(None, None, None) is None
    
    def test_convert_with_param_and_context(self):
        """Test convert method with parameter and context objects."""
        param_type = UnprocessedParamType()
        # Use Option instead of Parameter directly since Parameter is abstract
        mock_param = Option(["--test"])
        # Create a proper Command object for Context
        mock_command = Command("test_command")
        mock_ctx = Context(mock_command)
        
        test_value = "test_value"
        result = param_type.convert(test_value, mock_param, mock_ctx)
        assert result == test_value
    
    def test_repr_returns_unprocessed(self):
        """Test that __repr__ method returns 'UNPROCESSED'."""
        param_type = UnprocessedParamType()
        assert repr(param_type) == "UNPROCESSED"
    
    def test_name_attribute(self):
        """Test that the name attribute is set to 'text'."""
        param_type = UnprocessedParamType()
        assert param_type.name == "text"
