# file: src/click/src/click/exceptions.py:242-256
# asked: {"lines": [242, 243, 252, 253, 255, 256], "branches": []}
# gained: {"lines": [242, 243, 252, 253, 255, 256], "branches": []}

import pytest
from click.exceptions import BadOptionUsage
from click.core import Context, Command

class TestBadOptionUsage:
    def test_bad_option_usage_initialization_with_ctx(self):
        """Test BadOptionUsage initialization with context."""
        command = Command("test_command")
        ctx = Context(command)
        option_name = "test_option"
        message = "Invalid usage of option"
        
        exception = BadOptionUsage(option_name, message, ctx)
        
        assert exception.option_name == option_name
        assert exception.message == message
        assert exception.ctx == ctx
        assert exception.cmd == command

    def test_bad_option_usage_initialization_without_ctx(self):
        """Test BadOptionUsage initialization without context."""
        option_name = "test_option"
        message = "Invalid usage of option"
        
        exception = BadOptionUsage(option_name, message)
        
        assert exception.option_name == option_name
        assert exception.message == message
        assert exception.ctx is None
        assert exception.cmd is None

    def test_bad_option_usage_inheritance(self):
        """Test that BadOptionUsage properly inherits from UsageError."""
        option_name = "test_option"
        message = "Invalid usage of option"
        
        exception = BadOptionUsage(option_name, message)
        
        assert isinstance(exception, BadOptionUsage)
        assert hasattr(exception, 'option_name')
        assert exception.option_name == option_name
        assert exception.exit_code == 2  # Inherited from UsageError
