# file: src/click/src/click/exceptions.py:95-134
# asked: {"lines": [95, 96, 113, 116, 117, 118, 120, 121, 122, 124, 125, 126, 127, 128, 130, 132, 133], "branches": [[125, 126], [125, 127], [127, 128], [127, 130]]}
# gained: {"lines": [95, 96, 113, 116, 117, 118, 120, 121, 122, 124, 125, 126, 127, 128, 130, 132, 133], "branches": [[125, 126], [125, 127], [127, 128], [127, 130]]}

import pytest
from click.exceptions import BadParameter
from click.core import Context, Command, Option
import collections.abc as cabc


class TestBadParameter:
    def test_format_message_with_param_hint_string(self):
        """Test format_message when param_hint is a string."""
        exception = BadParameter("test message", param_hint="my_param")
        result = exception.format_message()
        expected = "Invalid value for my_param: test message"
        assert result == expected

    def test_format_message_with_param_hint_sequence(self):
        """Test format_message when param_hint is a sequence."""
        exception = BadParameter("test message", param_hint=["param1", "param2"])
        result = exception.format_message()
        expected = "Invalid value for 'param1' / 'param2': test message"
        assert result == expected

    def test_format_message_with_param(self, monkeypatch):
        """Test format_message when param is provided."""
        mock_param = Option(["--test-param"])
        
        def mock_get_error_hint(ctx):
            return "test_param_hint"
        
        monkeypatch.setattr(mock_param, "get_error_hint", mock_get_error_hint)
        
        exception = BadParameter("test message", param=mock_param)
        result = exception.format_message()
        expected = "Invalid value for test_param_hint: test message"
        assert result == expected

    def test_format_message_with_param_and_ctx(self, monkeypatch):
        """Test format_message when param and ctx are provided."""
        mock_param = Option(["--test-param"])
        mock_ctx = Context(Command("test_cmd"))
        
        def mock_get_error_hint(ctx):
            return "test_param_hint"
        
        monkeypatch.setattr(mock_param, "get_error_hint", mock_get_error_hint)
        
        exception = BadParameter("test message", ctx=mock_ctx, param=mock_param)
        result = exception.format_message()
        expected = "Invalid value for test_param_hint: test message"
        assert result == expected

    def test_format_message_with_no_param_or_hint(self):
        """Test format_message when neither param nor param_hint is provided."""
        exception = BadParameter("test message")
        result = exception.format_message()
        expected = "Invalid value: test message"
        assert result == expected

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        mock_ctx = Context(Command("test_cmd"))
        mock_param = Option(["--test-param"])
        
        exception = BadParameter(
            "test message", 
            ctx=mock_ctx, 
            param=mock_param, 
            param_hint="custom_hint"
        )
        
        assert exception.message == "test message"
        assert exception.ctx == mock_ctx
        assert exception.param == mock_param
        assert exception.param_hint == "custom_hint"
