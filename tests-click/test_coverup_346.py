# file: src/click/src/click/types.py:1041-1057
# asked: {"lines": [1041, 1054, 1056, 1057], "branches": []}
# gained: {"lines": [1041, 1054, 1056, 1057], "branches": []}

import pytest
from click.core import Context, Command, Argument
from click.types import Path
from click.shell_completion import CompletionItem


class TestPathShellComplete:
    """Test cases for Path.shell_complete method to achieve full coverage."""
    
    def test_shell_complete_dir_only(self):
        """Test shell_complete when dir_okay is True and file_okay is False."""
        path_type = Path(dir_okay=True, file_okay=False)
        command = Command("test_command")
        ctx = Context(command)
        param = Argument(["test_param"])
        incomplete = "some/path"
        
        result = path_type.shell_complete(ctx, param, incomplete)
        
        assert len(result) == 1
        assert isinstance(result[0], CompletionItem)
        assert result[0].value == incomplete
        assert result[0].type == "dir"
    
    def test_shell_complete_file_only(self):
        """Test shell_complete when dir_okay is False and file_okay is True."""
        path_type = Path(dir_okay=False, file_okay=True)
        command = Command("test_command")
        ctx = Context(command)
        param = Argument(["test_param"])
        incomplete = "some/file"
        
        result = path_type.shell_complete(ctx, param, incomplete)
        
        assert len(result) == 1
        assert isinstance(result[0], CompletionItem)
        assert result[0].value == incomplete
        assert result[0].type == "file"
    
    def test_shell_complete_both_file_and_dir(self):
        """Test shell_complete when both dir_okay and file_okay are True."""
        path_type = Path(dir_okay=True, file_okay=True)
        command = Command("test_command")
        ctx = Context(command)
        param = Argument(["test_param"])
        incomplete = "some/path"
        
        result = path_type.shell_complete(ctx, param, incomplete)
        
        assert len(result) == 1
        assert isinstance(result[0], CompletionItem)
        assert result[0].value == incomplete
        assert result[0].type == "file"
    
    def test_shell_complete_neither_file_nor_dir(self):
        """Test shell_complete when both dir_okay and file_okay are False."""
        path_type = Path(dir_okay=False, file_okay=False)
        command = Command("test_command")
        ctx = Context(command)
        param = Argument(["test_param"])
        incomplete = "some/path"
        
        result = path_type.shell_complete(ctx, param, incomplete)
        
        assert len(result) == 1
        assert isinstance(result[0], CompletionItem)
        assert result[0].value == incomplete
        assert result[0].type == "file"
    
    def test_shell_complete_empty_incomplete(self):
        """Test shell_complete with empty incomplete string."""
        path_type = Path(dir_okay=True, file_okay=False)
        command = Command("test_command")
        ctx = Context(command)
        param = Argument(["test_param"])
        incomplete = ""
        
        result = path_type.shell_complete(ctx, param, incomplete)
        
        assert len(result) == 1
        assert isinstance(result[0], CompletionItem)
        assert result[0].value == incomplete
        assert result[0].type == "dir"
