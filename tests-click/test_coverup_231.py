# file: src/click/src/click/shell_completion.py:244-254
# asked: {"lines": [244, 250, 251, 252, 253], "branches": []}
# gained: {"lines": [244, 250, 251, 252, 253], "branches": []}

import pytest
from click.shell_completion import ShellComplete
from click.core import Command
from unittest.mock import Mock

class TestShellCompleteSourceVars:
    def test_source_vars_returns_expected_dict(self):
        """Test that source_vars returns the expected dictionary with correct values."""
        # Create a mock command and context args
        mock_cli = Mock(spec=Command)
        mock_ctx_args = {}
        
        # Create ShellComplete instance with specific values
        shell_complete = ShellComplete(
            cli=mock_cli,
            ctx_args=mock_ctx_args,
            prog_name="test_prog",
            complete_var="TEST_COMPLETE_VAR"
        )
        
        # Call source_vars method
        result = shell_complete.source_vars()
        
        # Verify the returned dictionary contains the expected keys and values
        expected_func_name = "_test_prog_completion"
        assert result == {
            "complete_func": expected_func_name,
            "complete_var": "TEST_COMPLETE_VAR",
            "prog_name": "test_prog"
        }
        
        # Verify the func_name property was used correctly
        assert shell_complete.func_name == expected_func_name

    def test_source_vars_with_special_characters_in_prog_name(self):
        """Test source_vars with special characters in prog_name that get sanitized."""
        mock_cli = Mock(spec=Command)
        mock_ctx_args = {}
        
        # Create ShellComplete instance with special characters in prog_name
        shell_complete = ShellComplete(
            cli=mock_cli,
            ctx_args=mock_ctx_args,
            prog_name="my-test-program",
            complete_var="MY_TEST_COMPLETE"
        )
        
        result = shell_complete.source_vars()
        
        # Verify the func_name is properly sanitized
        expected_func_name = "_my_test_program_completion"
        assert result["complete_func"] == expected_func_name
        assert result["complete_var"] == "MY_TEST_COMPLETE"
        assert result["prog_name"] == "my-test-program"
