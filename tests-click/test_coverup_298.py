# file: src/click/src/click/shell_completion.py:283-289
# asked: {"lines": [283, 289], "branches": []}
# gained: {"lines": [283, 289], "branches": []}

import pytest
from click.shell_completion import ShellComplete, CompletionItem

class TestShellComplete:
    def test_format_completion_not_implemented(self):
        """Test that format_completion raises NotImplementedError when called on base class."""
        shell_complete = ShellComplete(cli=None, ctx_args={}, prog_name="test_prog", complete_var="_TEST_COMPLETE")
        item = CompletionItem(value="test_value")
        
        with pytest.raises(NotImplementedError):
            shell_complete.format_completion(item)
