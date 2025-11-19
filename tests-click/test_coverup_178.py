# file: src/click/src/click/exceptions.py:200-205
# asked: {"lines": [200, 201, 202, 203, 205], "branches": [[201, 202], [201, 205]]}
# gained: {"lines": [200, 201, 202, 203, 205], "branches": [[201, 202], [201, 205]]}

import pytest
from click.exceptions import MissingParameter
from click.core import Option

class TestMissingParameter:
    def test_missing_parameter_without_message_with_param(self):
        """Test MissingParameter.__str__ when no message is provided and param has a name."""
        param = Option(['--test-param'])
        exception = MissingParameter(param=param)
        result = str(exception)
        assert result == "Missing parameter: test_param"

    def test_missing_parameter_without_message_without_param(self):
        """Test MissingParameter.__str__ when no message is provided and param is None."""
        exception = MissingParameter()
        result = str(exception)
        assert result == "Missing parameter: None"

    def test_missing_parameter_with_message(self):
        """Test MissingParameter.__str__ when a custom message is provided."""
        exception = MissingParameter(message="Custom error message")
        result = str(exception)
        assert result == "Custom error message"
