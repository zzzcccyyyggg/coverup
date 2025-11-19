# file: src/click/src/click/shell_completion.py:271-281
# asked: {"lines": [271, 279, 280, 281], "branches": []}
# gained: {"lines": [271, 279, 280, 281], "branches": []}

import pytest
import click
from click.shell_completion import ShellComplete, CompletionItem
from click.core import Context, Command, Parameter
from click.types import Choice


class MockCommand(Command):
    """Mock command for testing shell completion."""
    
    def __init__(self, name, shell_complete_result=None):
        super().__init__(name)
        self.shell_complete_result = shell_complete_result or []
    
    def shell_complete(self, ctx, incomplete):
        return self.shell_complete_result


class TestShellCompleteCoverage:
    """Test cases to cover lines 271-281 in ShellComplete.get_completions."""
    
    def test_get_completions_with_command_completion(self):
        """Test get_completions when command handles completion."""
        # Create a command that returns completion items
        completion_items = [
            CompletionItem("value1"),
            CompletionItem("value2", type="file"),
            CompletionItem("value3", help="Help text")
        ]
        cmd = MockCommand("test_cmd", completion_items)
        
        # Create ShellComplete instance
        shell_complete = ShellComplete(cmd, {}, "test_prog", "TEST_VAR")
        
        # Call get_completions
        result = shell_complete.get_completions([], "incomplete")
        
        # Verify the completion items are returned
        assert result == completion_items
    
    def test_get_completions_with_parameter_completion(self):
        """Test get_completions when parameter handles completion."""
        # Create a command with a parameter that handles completion
        param_completion_items = [
            CompletionItem("param_value1"),
            CompletionItem("param_value2")
        ]
        
        # Create a command with a parameter that has custom shell completion
        cmd = click.Command("test_cmd", params=[
            click.Option(["--test-param"], 
                        shell_complete=lambda ctx, param, incomplete: param_completion_items)
        ])
        
        # Create ShellComplete instance
        shell_complete = ShellComplete(cmd, {}, "test_prog", "TEST_VAR")
        
        # Call get_completions with args that trigger parameter completion
        # This simulates completing a parameter value
        result = shell_complete.get_completions(["--test-param"], "incomp")
        
        # Verify the parameter's completion items are returned
        assert result == param_completion_items
    
    def test_get_completions_with_empty_incomplete(self):
        """Test get_completions with empty incomplete string."""
        completion_items = [
            CompletionItem("option1"),
            CompletionItem("option2")
        ]
        cmd = MockCommand("test_cmd", completion_items)
        
        shell_complete = ShellComplete(cmd, {}, "test_prog", "TEST_VAR")
        
        # Call with empty incomplete string
        result = shell_complete.get_completions([], "")
        
        assert result == completion_items
    
    def test_get_completions_with_nested_command(self):
        """Test get_completions with nested command structure."""
        # Create a subcommand that handles completion
        sub_completion_items = [
            CompletionItem("sub_value1"),
            CompletionItem("sub_value2")
        ]
        sub_cmd = MockCommand("sub_cmd", sub_completion_items)
        
        # Create a group command
        group_cmd = click.Group("group_cmd")
        group_cmd.add_command(sub_cmd)
        
        shell_complete = ShellComplete(group_cmd, {}, "test_prog", "TEST_VAR")
        
        # Call get_completions with args that navigate to subcommand
        result = shell_complete.get_completions(["sub_cmd"], "incomp")
        
        # Verify subcommand's completion items are returned
        assert result == sub_completion_items
    
    def test_get_completions_with_option_completion(self):
        """Test get_completions when completing option names."""
        completion_items = [
            CompletionItem("--verbose"),
            CompletionItem("--help")
        ]
        cmd = MockCommand("test_cmd", completion_items)
        
        shell_complete = ShellComplete(cmd, {}, "test_prog", "TEST_VAR")
        
        # Call with incomplete option (starts with dash)
        result = shell_complete.get_completions([], "--")
        
        assert result == completion_items
    
    def test_get_completions_with_choice_parameter(self):
        """Test get_completions with Choice parameter type."""
        # Create a command with Choice parameter
        cmd = click.Command("test_cmd", params=[
            click.Option(["--choice"], type=click.Choice(["option1", "option2", "option3"]))
        ])
        
        shell_complete = ShellComplete(cmd, {}, "test_prog", "TEST_VAR")
        
        # Call get_completions when completing choice parameter value
        result = shell_complete.get_completions(["--choice"], "opt")
        
        # Should return completion items for matching choices
        assert len(result) > 0
        assert all(isinstance(item, CompletionItem) for item in result)
        # Should include options starting with "opt"
        values = [item.value for item in result]
        assert "option1" in values
        assert "option2" in values
        assert "option3" in values
    
    def test_get_completions_with_argument_completion(self):
        """Test get_completions when argument handles completion."""
        # Create a command with an argument that has custom shell completion
        arg_completion_items = [
            CompletionItem("arg_value1"),
            CompletionItem("arg_value2")
        ]
        
        cmd = click.Command("test_cmd", params=[
            click.Argument(["filename"], 
                          shell_complete=lambda ctx, param, incomplete: arg_completion_items)
        ])
        
        shell_complete = ShellComplete(cmd, {}, "test_prog", "TEST_VAR")
        
        # Call get_completions with args that trigger argument completion
        result = shell_complete.get_completions([], "file")
        
        # Verify the argument's completion items are returned
        assert result == arg_completion_items
