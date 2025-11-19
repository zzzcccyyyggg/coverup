# file: src/click/src/click/types.py:712-724
# asked: {"lines": [712, 715, 716, 717, 718, 719, 720, 721, 722, 724], "branches": [[716, 717], [716, 724]]}
# gained: {"lines": [712, 715, 716, 717, 718, 719, 720, 721, 722], "branches": [[716, 717]]}

import pytest
from click.types import BoolParamType
from click.exceptions import BadParameter
from click.core import Context, Command

class TestBoolParamType:
    def test_convert_with_invalid_boolean_value(self):
        """Test that convert fails when str_to_bool returns None for invalid boolean value."""
        bool_type = BoolParamType()
        
        with pytest.raises(BadParameter) as exc_info:
            bool_type.convert("invalid_bool", None, None)
        
        expected_msg = "'invalid_bool' is not a valid boolean. Recognized values: , 0, 1, f, false, n, no, off, on, t, true, y, yes"
        assert expected_msg in str(exc_info.value)

    def test_convert_with_invalid_boolean_value_with_param_and_ctx(self):
        """Test that convert fails when str_to_bool returns None with param and context."""
        bool_type = BoolParamType()
        
        # Create proper mock parameter and context objects
        class MockParam:
            def __init__(self, name):
                self.name = name
        
        # Create a minimal command for the context
        class MockCommand(Command):
            def __init__(self):
                super().__init__(name="test_command")
        
        command = MockCommand()
        ctx = Context(command=command, info_name="test_command")
        param = MockParam("test_param")
        
        with pytest.raises(BadParameter) as exc_info:
            bool_type.convert("invalid_value", param, ctx)
        
        expected_msg = "'invalid_value' is not a valid boolean. Recognized values: , 0, 1, f, false, n, no, off, on, t, true, y, yes"
        assert expected_msg in str(exc_info.value)
