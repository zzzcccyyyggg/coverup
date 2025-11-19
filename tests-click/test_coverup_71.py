# file: src/click/src/click/shell_completion.py:363-396
# asked: {"lines": [363, 364, 366, 367, 369, 370, 371, 372, 374, 375, 376, 377, 379, 381, 382, 395, 396], "branches": []}
# gained: {"lines": [363, 364, 366, 367, 369, 370, 371, 372, 374, 375, 376, 377, 379, 381, 382, 395, 396], "branches": []}

import os
import pytest
from click.shell_completion import ZshComplete, CompletionItem
from click.core import Command
from click.testing import CliRunner

class TestZshComplete:
    def test_get_completion_args_with_incomplete(self, monkeypatch):
        """Test get_completion_args when COMP_WORDS has a word at COMP_CWORD index."""
        monkeypatch.setenv("COMP_WORDS", "test_command arg1 arg2 incomplete")
        monkeypatch.setenv("COMP_CWORD", "3")
        
        cli = Command("test_command")
        zsh_complete = ZshComplete(cli, {}, "test_command", "_TEST_COMPLETE")
        
        args, incomplete = zsh_complete.get_completion_args()
        
        assert args == ["arg1", "arg2"]
        assert incomplete == "incomplete"

    def test_get_completion_args_without_incomplete(self, monkeypatch):
        """Test get_completion_args when COMP_WORDS has no word at COMP_CWORD index."""
        monkeypatch.setenv("COMP_WORDS", "test_command arg1 arg2")
        monkeypatch.setenv("COMP_CWORD", "3")
        
        cli = Command("test_command")
        zsh_complete = ZshComplete(cli, {}, "test_command", "_TEST_COMPLETE")
        
        args, incomplete = zsh_complete.get_completion_args()
        
        assert args == ["arg1", "arg2"]
        assert incomplete == ""

    def test_format_completion_with_help_not_underscore(self):
        """Test format_completion when item.help is not '_' - colons should be escaped."""
        cli = Command("test_command")
        zsh_complete = ZshComplete(cli, {}, "test_command", "_TEST_COMPLETE")
        
        item = CompletionItem("file:name:with:colons", type="file", help="A file with colons")
        result = zsh_complete.format_completion(item)
        
        expected = "file\nfile\\:name\\:with\\:colons\nA file with colons"
        assert result == expected

    def test_format_completion_with_help_underscore(self):
        """Test format_completion when item.help is '_' - colons should NOT be escaped."""
        cli = Command("test_command")
        zsh_complete = ZshComplete(cli, {}, "test_command", "_TEST_COMPLETE")
        
        item = CompletionItem("file:name:with:colons", type="file", help="_")
        result = zsh_complete.format_completion(item)
        
        expected = "file\nfile:name:with:colons\n_"
        assert result == expected

    def test_format_completion_with_none_help(self):
        """Test format_completion when item.help is None - should be treated as '_'."""
        cli = Command("test_command")
        zsh_complete = ZshComplete(cli, {}, "test_command", "_TEST_COMPLETE")
        
        item = CompletionItem("file:name:with:colons", type="file", help=None)
        result = zsh_complete.format_completion(item)
        
        expected = "file\nfile:name:with:colons\n_"
        assert result == expected

    def test_format_completion_with_empty_help(self):
        """Test format_completion when item.help is empty string - should be treated as '_'."""
        cli = Command("test_command")
        zsh_complete = ZshComplete(cli, {}, "test_command", "_TEST_COMPLETE")
        
        item = CompletionItem("file:name:with:colons", type="file", help="")
        result = zsh_complete.format_completion(item)
        
        expected = "file\nfile:name:with:colons\n_"
        assert result == expected
