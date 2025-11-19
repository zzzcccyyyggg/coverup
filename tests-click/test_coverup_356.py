# file: src/click/src/click/types.py:95-100
# asked: {"lines": [95], "branches": []}
# gained: {"lines": [95], "branches": []}

import pytest
from click.core import Context, Option, Command
from click.types import ParamType

class TestParamTypeGetMissingMessage:
    """Test cases for ParamType.get_missing_message method."""
    
    def test_get_missing_message_returns_none_by_default(self):
        """Test that get_missing_message returns None by default."""
        param_type = ParamType()
        param = Option(['--test-param'])
        command = Command('test_command')
        ctx = Context(command)
        
        result = param_type.get_missing_message(param, ctx)
        
        assert result is None
