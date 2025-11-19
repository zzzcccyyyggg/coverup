# file: src/click/src/click/shell_completion.py:236-242
# asked: {"lines": [236, 237, 241, 242], "branches": []}
# gained: {"lines": [236, 237, 241, 242], "branches": []}

import pytest
import re
from click.shell_completion import ShellComplete
from click.core import Command

class TestShellComplete:
    def test_func_name_property(self):
        """Test that func_name property generates correct function name."""
        # Create a mock command
        mock_cli = Command('test-command')
        
        # Test with a simple program name
        shell_complete = ShellComplete(
            cli=mock_cli,
            ctx_args={},
            prog_name='myprog',
            complete_var='_MYPROG_COMPLETE'
        )
        
        # The func_name should be _myprog_completion
        assert shell_complete.func_name == '_myprog_completion'
        
        # Test with a program name containing hyphens
        shell_complete2 = ShellComplete(
            cli=mock_cli,
            ctx_args={},
            prog_name='my-test-prog',
            complete_var='_MY_TEST_PROG_COMPLETE'
        )
        
        # The func_name should be _my_test_prog_completion (hyphens replaced with underscores)
        assert shell_complete2.func_name == '_my_test_prog_completion'
        
        # Test with a program name containing non-word characters
        shell_complete3 = ShellComplete(
            cli=mock_cli,
            ctx_args={},
            prog_name='my@test$prog',
            complete_var='_MY_TEST_PROG_COMPLETE'
        )
        
        # The func_name should be _mytestprog_completion (non-word characters removed)
        assert shell_complete3.func_name == '_mytestprog_completion'
        
        # Test with empty program name
        shell_complete4 = ShellComplete(
            cli=mock_cli,
            ctx_args={},
            prog_name='',
            complete_var='_COMPLETE'
        )
        
        # The func_name should be __completion
        assert shell_complete4.func_name == '__completion'
