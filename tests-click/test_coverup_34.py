# file: src/click/src/click/shell_completion.py:399-423
# asked: {"lines": [399, 400, 402, 403, 405, 406, 407, 408, 409, 410, 414, 415, 417, 419, 420, 421, 423], "branches": [[408, 409], [408, 410], [414, 415], [414, 417], [420, 421], [420, 423]]}
# gained: {"lines": [399, 400, 402, 403, 405, 406, 407, 408, 409, 410, 414, 415, 417, 419, 420, 421, 423], "branches": [[408, 409], [408, 410], [414, 415], [414, 417], [420, 421], [420, 423]]}

import os
import pytest
from click.shell_completion import FishComplete, CompletionItem, split_arg_string


class TestFishComplete:
    """Test cases for FishComplete class to achieve full coverage."""
    
    def test_get_completion_args_with_incomplete_word(self, monkeypatch):
        """Test get_completion_args when COMP_CWORD contains an incomplete word."""
        monkeypatch.setenv("COMP_WORDS", "test_command arg1 arg2 'incomplete arg'")
        monkeypatch.setenv("COMP_CWORD", "'incomplete arg")
        
        complete = FishComplete(None, {}, "test_command", "_TEST_COMPLETE")
        args, incomplete = complete.get_completion_args()
        
        assert args == ["arg1", "arg2"]
        assert incomplete == "incomplete arg"
    
    def test_get_completion_args_with_empty_incomplete(self, monkeypatch):
        """Test get_completion_args when COMP_CWORD is empty."""
        monkeypatch.setenv("COMP_WORDS", "test_command arg1 arg2")
        monkeypatch.setenv("COMP_CWORD", "")
        
        complete = FishComplete(None, {}, "test_command", "_TEST_COMPLETE")
        args, incomplete = complete.get_completion_args()
        
        assert args == ["arg1", "arg2"]
        assert incomplete == ""
    
    def test_get_completion_args_removes_incomplete_from_args(self, monkeypatch):
        """Test get_completion_args removes incomplete word from args when it matches."""
        monkeypatch.setenv("COMP_WORDS", "test_command arg1 arg2 incomplete")
        monkeypatch.setenv("COMP_CWORD", "incomplete")
        
        complete = FishComplete(None, {}, "test_command", "_TEST_COMPLETE")
        args, incomplete = complete.get_completion_args()
        
        assert args == ["arg1", "arg2"]
        assert incomplete == "incomplete"
    
    def test_get_completion_args_does_not_remove_when_no_match(self, monkeypatch):
        """Test get_completion_args does not remove incomplete word when it doesn't match args."""
        monkeypatch.setenv("COMP_WORDS", "test_command arg1 arg2 different")
        monkeypatch.setenv("COMP_CWORD", "incomplete")
        
        complete = FishComplete(None, {}, "test_command", "_TEST_COMPLETE")
        args, incomplete = complete.get_completion_args()
        
        assert args == ["arg1", "arg2", "different"]
        assert incomplete == "incomplete"
    
    def test_format_completion_with_help(self):
        """Test format_completion when item has help text."""
        item = CompletionItem("test_value", type="file", help="Test help text")
        complete = FishComplete(None, {}, "test_command", "_TEST_COMPLETE")
        
        result = complete.format_completion(item)
        
        assert result == "file,test_value\tTest help text"
    
    def test_format_completion_without_help(self):
        """Test format_completion when item has no help text."""
        item = CompletionItem("test_value", type="dir")
        complete = FishComplete(None, {}, "test_command", "_TEST_COMPLETE")
        
        result = complete.format_completion(item)
        
        assert result == "dir,test_value"
