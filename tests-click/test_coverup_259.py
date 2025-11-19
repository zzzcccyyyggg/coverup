# file: src/click/src/click/shell_completion.py:291-301
# asked: {"lines": [291, 298, 299, 300, 301], "branches": []}
# gained: {"lines": [291, 298, 299, 300, 301], "branches": []}

import pytest
from click.shell_completion import ShellComplete, CompletionItem
from click.core import Command
from unittest.mock import Mock, MagicMock

class TestShellComplete:
    def test_complete_method_executes_all_lines(self, monkeypatch):
        """Test that the complete method executes lines 291-301."""
        # Create a mock command and context args
        mock_cli = Mock(spec=Command)
        ctx_args = {}
        prog_name = "test_prog"
        complete_var = "_TEST_COMPLETE"
        
        # Create instance of ShellComplete
        shell_complete = ShellComplete(mock_cli, ctx_args, prog_name, complete_var)
        
        # Mock the methods called in complete()
        mock_args = ["arg1", "arg2"]
        mock_incomplete = "incomplete"
        mock_completions = [
            CompletionItem("value1"),
            CompletionItem("value2"),
            CompletionItem("value3")
        ]
        
        # Mock get_completion_args to return our test data
        monkeypatch.setattr(shell_complete, 'get_completion_args', 
                           Mock(return_value=(mock_args, mock_incomplete)))
        
        # Mock get_completions to return our test completions
        monkeypatch.setattr(shell_complete, 'get_completions', 
                           Mock(return_value=mock_completions))
        
        # Mock format_completion to return the value directly
        monkeypatch.setattr(shell_complete, 'format_completion', 
                           Mock(side_effect=lambda item: item.value))
        
        # Call the complete method
        result = shell_complete.complete()
        
        # Verify all methods were called correctly
        shell_complete.get_completion_args.assert_called_once()
        shell_complete.get_completions.assert_called_once_with(mock_args, mock_incomplete)
        
        # Verify format_completion was called for each completion item
        assert shell_complete.format_completion.call_count == 3
        shell_complete.format_completion.assert_any_call(mock_completions[0])
        shell_complete.format_completion.assert_any_call(mock_completions[1])
        shell_complete.format_completion.assert_any_call(mock_completions[2])
        
        # Verify the result is correctly formatted
        expected_result = "value1\nvalue2\nvalue3"
        assert result == expected_result

    def test_complete_with_empty_completions(self, monkeypatch):
        """Test complete method when there are no completions."""
        mock_cli = Mock(spec=Command)
        ctx_args = {}
        prog_name = "test_prog"
        complete_var = "_TEST_COMPLETE"
        
        shell_complete = ShellComplete(mock_cli, ctx_args, prog_name, complete_var)
        
        # Mock methods to return empty completions
        monkeypatch.setattr(shell_complete, 'get_completion_args', 
                           Mock(return_value=([], "")))
        monkeypatch.setattr(shell_complete, 'get_completions', 
                           Mock(return_value=[]))
        monkeypatch.setattr(shell_complete, 'format_completion', 
                           Mock())
        
        # Call complete method
        result = shell_complete.complete()
        
        # Verify methods were called
        shell_complete.get_completion_args.assert_called_once()
        shell_complete.get_completions.assert_called_once_with([], "")
        shell_complete.format_completion.assert_not_called()  # No completions to format
        
        # Result should be empty string
        assert result == ""

    def test_complete_with_completion_items_having_different_formats(self, monkeypatch):
        """Test complete method with CompletionItems that have different formats."""
        mock_cli = Mock(spec=Command)
        ctx_args = {}
        prog_name = "test_prog"
        complete_var = "_TEST_COMPLETE"
        
        shell_complete = ShellComplete(mock_cli, ctx_args, prog_name, complete_var)
        
        # Mock get_completion_args
        monkeypatch.setattr(shell_complete, 'get_completion_args', 
                           Mock(return_value=(["test"], "cmd")))
        
        # Create CompletionItems with different types and help
        mock_completions = [
            CompletionItem("file1.txt", type="file", help="A text file"),
            CompletionItem("/path/to/dir", type="dir", help="A directory"),
            CompletionItem("plain_value", type="plain")
        ]
        
        monkeypatch.setattr(shell_complete, 'get_completions', 
                           Mock(return_value=mock_completions))
        
        # Mock format_completion to return formatted strings
        def mock_format(item):
            if item.type == "file":
                return f"FILE:{item.value}"
            elif item.type == "dir":
                return f"DIR:{item.value}"
            else:
                return item.value
        
        monkeypatch.setattr(shell_complete, 'format_completion', 
                           Mock(side_effect=mock_format))
        
        # Call complete method
        result = shell_complete.complete()
        
        # Verify the result contains all formatted completions
        expected_lines = [
            "FILE:file1.txt",
            "DIR:/path/to/dir", 
            "plain_value"
        ]
        expected_result = "\n".join(expected_lines)
        assert result == expected_result
        
        # Verify format_completion was called for each item
        assert shell_complete.format_completion.call_count == 3
