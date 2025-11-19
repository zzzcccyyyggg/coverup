# file: src/click/src/click/core.py:1271-1316
# asked: {"lines": [1271, 1283, 1285, 1287, 1288, 1289, 1290, 1291, 1293, 1294, 1295, 1298, 1300, 1301, 1302, 1303, 1306, 1307, 1309, 1310, 1311, 1312, 1313, 1316], "branches": [[1287, 1288], [1287, 1306], [1288, 1289], [1288, 1306], [1289, 1298], [1289, 1300], [1306, 1307], [1306, 1316], [1309, 1306], [1309, 1310]]}
# gained: {"lines": [1271, 1283, 1285, 1287, 1288, 1289, 1290, 1291, 1293, 1294, 1295, 1298, 1300, 1301, 1302, 1303, 1306, 1307, 1309, 1310, 1311, 1312, 1313, 1316], "branches": [[1287, 1288], [1287, 1306], [1288, 1289], [1288, 1306], [1289, 1298], [1289, 1300], [1306, 1307], [1306, 1316], [1309, 1306], [1309, 1310]]}

import pytest
import click
from click.core import Command, Group, Option, Context, ParameterSource
from click.shell_completion import CompletionItem


class TestCommandShellComplete:
    """Test cases for Command.shell_complete method to achieve full coverage."""
    
    def test_shell_complete_with_non_alphanumeric_incomplete_and_options(self, monkeypatch):
        """Test shell_complete with non-alphanumeric incomplete and options that should be completed."""
        cmd = Command('test_cmd')
        
        # Create an option that should be included in completions
        option = Option(['--test-option'], help='Test option help')
        cmd.params = [option]
        
        # Create a context where the option hasn't been provided via commandline
        ctx = Context(cmd)
        
        # Mock get_parameter_source to return None (not provided via commandline)
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: None)
        
        # Call shell_complete with non-alphanumeric incomplete
        result = cmd.shell_complete(ctx, '--')
        
        # Should return CompletionItem for the option
        # Note: Command may have a help option added automatically
        option_completions = [item for item in result if item.value == '--test-option']
        assert len(option_completions) == 1
        assert isinstance(option_completions[0], CompletionItem)
        assert option_completions[0].help == 'Test option help'
    
    def test_shell_complete_with_non_alphanumeric_incomplete_and_hidden_option(self, monkeypatch):
        """Test shell_complete with non-alphanumeric incomplete and hidden options that should be skipped."""
        cmd = Command('test_cmd')
        
        # Create a hidden option that should NOT be included in completions
        hidden_option = Option(['--hidden-opt'], help='Hidden option', hidden=True)
        cmd.params = [hidden_option]
        
        ctx = Context(cmd)
        # Mock get_parameter_source to return None
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: None)
        
        result = cmd.shell_complete(ctx, '--')
        
        # Hidden option should not be in results
        hidden_completions = [item for item in result if item.value == '--hidden-opt']
        assert len(hidden_completions) == 0
    
    def test_shell_complete_with_non_alphanumeric_incomplete_and_already_provided_option(self, monkeypatch):
        """Test shell_complete with non-alphanumeric incomplete and options already provided via commandline."""
        cmd = Command('test_cmd')
        
        # Create an option
        option = Option(['--provided-opt'], help='Already provided option')
        cmd.params = [option]
        
        # Create a context where the option has been provided via commandline
        ctx = Context(cmd)
        # Mock get_parameter_source to return COMMANDLINE
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: ParameterSource.COMMANDLINE)
        
        result = cmd.shell_complete(ctx, '--')
        
        # Option already provided should not be in results
        provided_completions = [item for item in result if item.value == '--provided-opt']
        assert len(provided_completions) == 0
    
    def test_shell_complete_with_non_alphanumeric_incomplete_and_multiple_option(self, monkeypatch):
        """Test shell_complete with non-alphanumeric incomplete and multiple options."""
        cmd = Command('test_cmd')
        
        # Create a multiple option (can be provided multiple times)
        multiple_option = Option(['--multi-opt'], help='Multiple option', multiple=True)
        cmd.params = [multiple_option]
        
        ctx = Context(cmd)
        # Mock get_parameter_source to return COMMANDLINE
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: ParameterSource.COMMANDLINE)
        
        result = cmd.shell_complete(ctx, '--')
        
        # Multiple option should still be in results even if already provided
        multi_completions = [item for item in result if item.value == '--multi-opt']
        assert len(multi_completions) == 1
        assert multi_completions[0].value == '--multi-opt'
    
    def test_shell_complete_with_chained_commands(self):
        """Test shell_complete with parent context containing chained commands."""
        # Create parent group with chain=True
        parent_group = Group('parent', chain=True)
        child_cmd1 = Command('child1', help='First child command')
        child_cmd2 = Command('child2', help='Second child command')
        parent_group.add_command(child_cmd1)
        parent_group.add_command(child_cmd2)
        
        # Create current command
        current_cmd = Command('current')
        
        # Create context hierarchy
        parent_ctx = Context(parent_group)
        ctx = Context(current_cmd, parent=parent_ctx)
        
        # Call shell_complete with incomplete that matches child commands
        result = current_cmd.shell_complete(ctx, 'child')
        
        # Should return CompletionItems for sibling commands that match
        assert len(result) == 2
        completions = {item.value: item for item in result}
        assert 'child1' in completions
        assert 'child2' in completions
        assert completions['child1'].help == 'First child command'
        assert completions['child2'].help == 'Second child command'
    
    def test_shell_complete_with_chained_commands_and_protected_args(self):
        """Test shell_complete with parent context containing chained commands and protected args."""
        # Create parent group with chain=True
        parent_group = Group('parent', chain=True)
        child_cmd1 = Command('child1', help='First child command')
        child_cmd2 = Command('child2', help='Second child command')
        parent_group.add_command(child_cmd1)
        parent_group.add_command(child_cmd2)
        
        # Create current command
        current_cmd = Command('current')
        
        # Create context hierarchy with protected args
        parent_ctx = Context(parent_group)
        parent_ctx._protected_args = {'child1'}  # Protect child1 from completion
        ctx = Context(current_cmd, parent=parent_ctx)
        
        # Call shell_complete with incomplete that matches child commands
        result = current_cmd.shell_complete(ctx, 'child')
        
        # Should only return child2 since child1 is protected
        assert len(result) == 1
        assert result[0].value == 'child2'
    
    def test_shell_complete_with_empty_incomplete(self, monkeypatch):
        """Test shell_complete with empty incomplete string."""
        cmd = Command('test_cmd')
        
        # Create an option
        option = Option(['--test-option'], help='Test option')
        cmd.params = [option]
        
        ctx = Context(cmd)
        # Mock get_parameter_source to return None
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: None)
        
        # Call with empty incomplete - should skip option completion part
        result = cmd.shell_complete(ctx, '')
        
        # Empty incomplete should not trigger option completion
        option_completions = [item for item in result if item.value == '--test-option']
        assert len(option_completions) == 0
    
    def test_shell_complete_with_alphanumeric_incomplete(self, monkeypatch):
        """Test shell_complete with alphanumeric incomplete string."""
        cmd = Command('test_cmd')
        
        # Create an option
        option = Option(['--test-option'], help='Test option')
        cmd.params = [option]
        
        ctx = Context(cmd)
        # Mock get_parameter_source to return None
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: None)
        
        # Call with alphanumeric incomplete - should skip option completion part
        result = cmd.shell_complete(ctx, 'test')
        
        # Alphanumeric incomplete should not trigger option completion
        option_completions = [item for item in result if item.value == '--test-option']
        assert len(option_completions) == 0
    
    def test_shell_complete_with_option_secondary_opts(self, monkeypatch):
        """Test shell_complete includes both primary and secondary opts."""
        cmd = Command('test_cmd')
        
        # Create an option with both primary and secondary opts
        option = Option(['-t', '--test'], help='Test option with short and long forms')
        cmd.params = [option]
        
        ctx = Context(cmd)
        # Mock get_parameter_source to return None
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: None)
        
        result = cmd.shell_complete(ctx, '-')
        
        # Should include both short and long forms
        option_completions = [item for item in result if item.value in ['-t', '--test']]
        assert len(option_completions) == 2
        values = {item.value for item in option_completions}
        assert '-t' in values
        assert '--test' in values
    
    def test_shell_complete_with_multiple_parent_levels(self):
        """Test shell_complete traverses multiple parent levels to find chained commands."""
        # Create grandparent group with chain=True
        grandparent_group = Group('grandparent', chain=True)
        parent_cmd = Command('parent_cmd')
        grandparent_group.add_command(parent_cmd)
        
        # Create parent group (not chained)
        parent_group = Group('parent')
        current_cmd = Command('current')
        parent_group.add_command(current_cmd)
        
        # Create context hierarchy: current -> parent -> grandparent
        grandparent_ctx = Context(grandparent_group)
        parent_ctx = Context(parent_group, parent=grandparent_ctx)
        ctx = Context(current_cmd, parent=parent_ctx)
        
        # Call shell_complete - should traverse to grandparent for chained commands
        result = current_cmd.shell_complete(ctx, 'parent')
        
        # Should find parent_cmd from grandparent level
        assert len(result) == 1
        assert result[0].value == 'parent_cmd'
    
    def test_shell_complete_with_non_option_parameter(self, monkeypatch):
        """Test shell_complete skips non-Option parameters."""
        cmd = Command('test_cmd')
        
        # Create a non-Option parameter (like Argument)
        from click.core import Argument
        argument = Argument(['arg_name'])
        cmd.params = [argument]
        
        ctx = Context(cmd)
        # Mock get_parameter_source to return None
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: None)
        
        result = cmd.shell_complete(ctx, '--')
        
        # Non-Option parameters should be skipped
        # Note: Command may have a help option added automatically
        argument_completions = [item for item in result if item.value == 'arg_name']
        assert len(argument_completions) == 0
    
    def test_shell_complete_with_option_not_matching_incomplete(self, monkeypatch):
        """Test shell_complete with options that don't match the incomplete prefix."""
        cmd = Command('test_cmd')
        
        # Create an option
        option = Option(['--test-option'], help='Test option')
        cmd.params = [option]
        
        ctx = Context(cmd)
        # Mock get_parameter_source to return None
        monkeypatch.setattr(ctx, 'get_parameter_source', lambda name: None)
        
        # Call with incomplete that doesn't match the option
        result = cmd.shell_complete(ctx, '--xyz')
        
        # Option should not be in results since it doesn't match the incomplete
        option_completions = [item for item in result if item.value == '--test-option']
        assert len(option_completions) == 0
