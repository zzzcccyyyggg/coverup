# file: src/click/src/click/core.py:1451-1481
# asked: {"lines": [1451, 1455, 1469, 1470, 1471, 1473, 1475, 1476, 1478, 1480, 1481], "branches": [[1469, 1470], [1469, 1473], [1475, 1476], [1475, 1478]]}
# gained: {"lines": [1451, 1455, 1469, 1470, 1471, 1473, 1475, 1476, 1478, 1480, 1481], "branches": [[1469, 1470], [1469, 1473], [1475, 1476], [1475, 1478]]}

import os
import sys
import pytest
from unittest.mock import Mock, patch
from click.core import Command


class TestCommandShellCompletion:
    """Test cases for Command._main_shell_completion method to achieve full coverage."""
    
    def test_main_shell_completion_no_complete_var_no_instruction(self, monkeypatch):
        """Test when complete_var is None and no instruction in environment."""
        command = Command("test_command")
        ctx_args = {}
        prog_name = "test-prog"
        
        # Remove any completion environment variable
        monkeypatch.delenv("_TEST_PROG_COMPLETE", raising=False)
        
        # Should return early without calling shell_complete
        command._main_shell_completion(ctx_args, prog_name)
        # No assertion needed - just verifying no exception and early return
    
    def test_main_shell_completion_with_complete_var_no_instruction(self, monkeypatch):
        """Test when complete_var is provided but no instruction in environment."""
        command = Command("test_command")
        ctx_args = {}
        prog_name = "test-prog"
        complete_var = "CUSTOM_COMPLETE_VAR"
        
        # Remove the custom completion environment variable
        monkeypatch.delenv(complete_var, raising=False)
        
        # Should return early without calling shell_complete
        command._main_shell_completion(ctx_args, prog_name, complete_var)
        # No assertion needed - just verifying no exception and early return
    
    def test_main_shell_completion_with_instruction_exits(self, monkeypatch):
        """Test when instruction is present in environment - should call shell_complete and exit."""
        command = Command("test_command")
        ctx_args = {}
        prog_name = "test-prog"
        complete_var = "_TEST_PROG_COMPLETE"
        instruction = "bash_complete"
        
        # Set the completion environment variable
        monkeypatch.setenv(complete_var, instruction)
        
        # Mock shell_complete to return a specific exit code
        mock_shell_complete = Mock(return_value=42)
        
        # Mock sys.exit to capture the exit call
        mock_exit = Mock()
        
        with patch('click.shell_completion.shell_complete', mock_shell_complete):
            with patch('sys.exit', mock_exit):
                command._main_shell_completion(ctx_args, prog_name, complete_var)
        
        # Verify shell_complete was called with correct arguments
        mock_shell_complete.assert_called_once_with(
            command, ctx_args, prog_name, complete_var, instruction
        )
        # Verify sys.exit was called with the return value from shell_complete
        mock_exit.assert_called_once_with(42)
    
    def test_main_shell_completion_prog_name_with_dots_and_dashes(self, monkeypatch):
        """Test that prog_name with dots and dashes is properly converted to complete_var."""
        command = Command("test_command")
        ctx_args = {}
        prog_name = "my-test.program"
        instruction = "zsh_complete"
        
        # Set the expected environment variable (dots and dashes replaced with underscores)
        expected_complete_var = "_MY_TEST_PROGRAM_COMPLETE"
        monkeypatch.setenv(expected_complete_var, instruction)
        
        # Mock shell_complete to return a specific exit code
        mock_shell_complete = Mock(return_value=0)
        mock_exit = Mock()
        
        with patch('click.shell_completion.shell_complete', mock_shell_complete):
            with patch('sys.exit', mock_exit):
                command._main_shell_completion(ctx_args, prog_name)
        
        # Verify shell_complete was called with the generated complete_var
        mock_shell_complete.assert_called_once()
        call_args = mock_shell_complete.call_args[0]
        assert call_args[3] == expected_complete_var  # complete_var argument
        assert call_args[4] == instruction  # instruction argument
    
    def test_main_shell_completion_with_custom_complete_var_and_instruction(self, monkeypatch):
        """Test when both complete_var and instruction are provided."""
        command = Command("test_command")
        ctx_args = {}
        prog_name = "test-prog"
        complete_var = "MY_CUSTOM_COMPLETE"
        instruction = "fish_source"
        
        # Set the custom completion environment variable
        monkeypatch.setenv(complete_var, instruction)
        
        # Mock shell_complete to return a specific exit code
        mock_shell_complete = Mock(return_value=123)
        mock_exit = Mock()
        
        with patch('click.shell_completion.shell_complete', mock_shell_complete):
            with patch('sys.exit', mock_exit):
                command._main_shell_completion(ctx_args, prog_name, complete_var)
        
        # Verify shell_complete was called with correct arguments
        mock_shell_complete.assert_called_once_with(
            command, ctx_args, prog_name, complete_var, instruction
        )
        # Verify sys.exit was called with the return value from shell_complete
        mock_exit.assert_called_once_with(123)
