# file: src/click/src/click/types.py:136-143
# asked: {"lines": [136, 139, 140, 143], "branches": []}
# gained: {"lines": [136, 139, 140, 143], "branches": []}

import pytest
from click.types import ParamType
from click.exceptions import BadParameter
from click.core import Context, Command

class MockCommand(Command):
    """A mock command for testing."""
    def __init__(self, name="test_command"):
        super().__init__(name=name)

class TestParamType:
    def test_fail_with_message_only(self):
        """Test that fail raises BadParameter with only message."""
        param_type = ParamType()
        with pytest.raises(BadParameter) as exc_info:
            param_type.fail("Test error message")
        assert str(exc_info.value) == "Test error message"
        assert exc_info.value.param is None
        assert exc_info.value.ctx is None

    def test_fail_with_message_and_param(self):
        """Test that fail raises BadParameter with message and param."""
        param_type = ParamType()
        mock_param = object()
        with pytest.raises(BadParameter) as exc_info:
            param_type.fail("Test error with param", param=mock_param)
        assert str(exc_info.value) == "Test error with param"
        assert exc_info.value.param is mock_param
        assert exc_info.value.ctx is None

    def test_fail_with_message_and_ctx(self):
        """Test that fail raises BadParameter with message and ctx."""
        param_type = ParamType()
        mock_command = MockCommand()
        mock_ctx = Context(command=mock_command)
        with pytest.raises(BadParameter) as exc_info:
            param_type.fail("Test error with ctx", ctx=mock_ctx)
        assert str(exc_info.value) == "Test error with ctx"
        assert exc_info.value.param is None
        assert exc_info.value.ctx is mock_ctx
        assert exc_info.value.cmd is mock_command

    def test_fail_with_all_parameters(self):
        """Test that fail raises BadParameter with all parameters."""
        param_type = ParamType()
        mock_param = object()
        mock_command = MockCommand()
        mock_ctx = Context(command=mock_command)
        with pytest.raises(BadParameter) as exc_info:
            param_type.fail("Test error with all", param=mock_param, ctx=mock_ctx)
        assert str(exc_info.value) == "Test error with all"
        assert exc_info.value.param is mock_param
        assert exc_info.value.ctx is mock_ctx
        assert exc_info.value.cmd is mock_command
