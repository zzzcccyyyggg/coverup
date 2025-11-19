# file: src/click/src/click/types.py:92-93
# asked: {"lines": [92], "branches": []}
# gained: {"lines": [92], "branches": []}

import pytest
from click.core import Context, Option, Command
from click.types import ParamType

class TestParamTypeGetMetavar:
    """Test cases for ParamType.get_metavar method."""
    
    def test_get_metavar_returns_none_by_default(self):
        """Test that get_metavar returns None by default."""
        # Arrange
        param_type = ParamType()
        param = Option(['--test-param'])
        command = Command('test_command')
        ctx = Context(command)
        
        # Act
        result = param_type.get_metavar(param, ctx)
        
        # Assert
        assert result is None
