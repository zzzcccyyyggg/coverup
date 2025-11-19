# file: src/click/src/click/shell_completion.py:256-262
# asked: {"lines": [256, 262], "branches": []}
# gained: {"lines": [256, 262], "branches": []}

import pytest
from click.shell_completion import ShellComplete
from click.core import Command

class TestShellCompleteSource:
    def test_source_method_executes(self, monkeypatch):
        """Test that ShellComplete.source() method executes lines 256-262."""
        # Create a mock command and context args
        mock_cli = Command('test_command')
        ctx_args = {}
        prog_name = 'test_prog'
        complete_var = '_TEST_COMPLETE'
        
        # Create a concrete subclass to test the source method
        class TestShellComplete(ShellComplete):
            name = 'test'
            source_template = 'test_template with %(complete_func)s %(complete_var)s %(prog_name)s'
            
            @property
            def func_name(self):
                return 'test_complete_func'
        
        # Create instance
        shell_complete = TestShellComplete(mock_cli, ctx_args, prog_name, complete_var)
        
        # Call the source method
        result = shell_complete.source()
        
        # Verify the result is formatted correctly using the template and source_vars
        expected = 'test_template with test_complete_func _TEST_COMPLETE test_prog'
        assert result == expected
