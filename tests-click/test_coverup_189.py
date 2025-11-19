# file: src/click/src/click/exceptions.py:149-158
# asked: {"lines": [149, 151, 152, 153, 154, 155, 157, 158], "branches": []}
# gained: {"lines": [149, 151, 152, 153, 154, 155, 157, 158], "branches": []}

import pytest
from click.exceptions import MissingParameter
from click.core import Context, Command, Option, Argument


class TestMissingParameter:
    def test_init_with_param_type(self):
        """Test that MissingParameter correctly sets param_type when provided."""
        param_type = "option"
        exception = MissingParameter(param_type=param_type)
        assert exception.param_type == param_type

    def test_init_with_message_and_param_type(self):
        """Test that MissingParameter correctly handles both message and param_type."""
        message = "Custom error message"
        param_type = "argument"
        exception = MissingParameter(message=message, param_type=param_type)
        assert exception.message == message
        assert exception.param_type == param_type

    def test_init_with_all_parameters(self):
        """Test MissingParameter initialization with all optional parameters."""
        message = "Missing required parameter"
        command = Command("test_command")
        ctx = Context(command)
        param = Option(["--test-param"])
        param_hint = "test_param_hint"
        param_type = "parameter"
        
        exception = MissingParameter(
            message=message,
            ctx=ctx,
            param=param,
            param_hint=param_hint,
            param_type=param_type
        )
        
        assert exception.message == message
        assert exception.ctx == ctx
        assert exception.param == param
        assert exception.param_hint == param_hint
        assert exception.param_type == param_type

    def test_init_with_none_message(self):
        """Test that MissingParameter uses empty string when message is None."""
        exception = MissingParameter(message=None)
        assert exception.message == ""
        assert exception.param_type is None

    def test_init_with_empty_message(self):
        """Test that MissingParameter preserves empty message string."""
        exception = MissingParameter(message="")
        assert exception.message == ""
        assert exception.param_type is None

    def test_init_with_argument_param(self):
        """Test MissingParameter with Argument parameter."""
        message = "Missing argument"
        command = Command("test_command")
        ctx = Context(command)
        param = Argument(["test_arg"])
        param_type = "argument"
        
        exception = MissingParameter(
            message=message,
            ctx=ctx,
            param=param,
            param_type=param_type
        )
        
        assert exception.message == message
        assert exception.ctx == ctx
        assert exception.param == param
        assert exception.param_type == param_type
