# file: src/click/src/click/core.py:718-724
# asked: {"lines": [718, 724], "branches": []}
# gained: {"lines": [718, 724], "branches": []}

import pytest
from click.core import Context, Command
from click.exceptions import UsageError

class TestContextFail:
    def test_fail_raises_usage_error_with_message_and_context(self):
        """Test that Context.fail raises UsageError with correct message and context."""
        # Create a minimal Command instance with required attributes
        class MockCommand(Command):
            def __init__(self):
                super().__init__(name="test_command")
        
        cmd = MockCommand()
        ctx = Context(command=cmd)
        
        # Test that fail raises UsageError with the provided message and context
        with pytest.raises(UsageError) as exc_info:
            ctx.fail("Test error message")
        
        # Verify the exception has the correct message and context
        assert exc_info.value.message == "Test error message"
        assert exc_info.value.ctx is ctx
