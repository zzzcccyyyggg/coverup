# file: src/click/src/click/core.py:726-728
# asked: {"lines": [726, 728], "branches": []}
# gained: {"lines": [726, 728], "branches": []}

import pytest
from click.core import Context, Command
from click.exceptions import Abort

class TestContextAbort:
    def test_abort_raises_abort_exception(self):
        """Test that Context.abort() raises Abort exception."""
        # Create a minimal Command instance to pass to Context
        cmd = Command(name="test_command")
        ctx = Context(command=cmd)
        
        with pytest.raises(Abort):
            ctx.abort()
