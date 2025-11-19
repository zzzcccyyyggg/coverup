# file: src/click/src/click/core.py:1797-1823
# asked: {"lines": [1797, 1801, 1802, 1803, 1805, 1806, 1807, 1808, 1810, 1813, 1814, 1816, 1817, 1818, 1819, 1821, 1822, 1823], "branches": [[1802, 1803], [1802, 1813], [1805, 1806], [1805, 1807], [1807, 1808], [1807, 1810], [1813, 0], [1813, 1814], [1817, 1818], [1817, 1821], [1821, 0], [1821, 1822]]}
# gained: {"lines": [1797, 1801, 1802, 1803, 1805, 1806, 1807, 1808, 1810, 1813, 1814, 1816, 1817, 1818, 1819, 1821, 1822, 1823], "branches": [[1802, 1803], [1802, 1813], [1805, 1806], [1805, 1807], [1807, 1808], [1807, 1810], [1813, 0], [1813, 1814], [1817, 1818], [1817, 1821], [1821, 1822]]}

import pytest
from click.core import Group, Command, Context
from click.formatting import HelpFormatter
from unittest.mock import Mock, MagicMock


class TestGroupFormatCommands:
    """Test cases for Group.format_commands method to achieve full coverage."""
    
    def test_format_commands_empty_commands_list(self):
        """Test when there are no commands to format."""
        group = Group("test_group")
        ctx = Mock(spec=Context)
        formatter = Mock(spec=HelpFormatter)
        
        # Mock list_commands to return empty list
        group.list_commands = Mock(return_value=[])
        
        group.format_commands(ctx, formatter)
        
        # Verify no sections were written
        formatter.section.assert_not_called()
        formatter.write_dl.assert_not_called()
    
    def test_format_commands_with_none_command(self):
        """Test when get_command returns None for a subcommand."""
        group = Group("test_group")
        ctx = Mock(spec=Context)
        formatter = Mock(spec=HelpFormatter)
        
        # Mock list_commands to return a subcommand
        group.list_commands = Mock(return_value=["nonexistent"])
        # Mock get_command to return None
        group.get_command = Mock(return_value=None)
        
        group.format_commands(ctx, formatter)
        
        # Verify no sections were written since command was None
        formatter.section.assert_not_called()
        formatter.write_dl.assert_not_called()
    
    def test_format_commands_with_hidden_command(self):
        """Test when a command is hidden."""
        group = Group("test_group")
        ctx = Mock(spec=Context)
        formatter = Mock(spec=HelpFormatter)
        
        # Create a hidden command
        hidden_cmd = Mock(spec=Command)
        hidden_cmd.hidden = True
        
        # Mock list_commands to return a subcommand
        group.list_commands = Mock(return_value=["hidden_cmd"])
        # Mock get_command to return the hidden command
        group.get_command = Mock(return_value=hidden_cmd)
        
        group.format_commands(ctx, formatter)
        
        # Verify no sections were written since command was hidden
        formatter.section.assert_not_called()
        formatter.write_dl.assert_not_called()
    
    def test_format_commands_with_valid_commands(self):
        """Test when there are valid commands to format."""
        group = Group("test_group")
        ctx = Mock(spec=Context)
        formatter = Mock(spec=HelpFormatter)
        
        # Create mock commands
        cmd1 = Mock(spec=Command)
        cmd1.hidden = False
        cmd1.get_short_help_str = Mock(return_value="Help for command 1")
        
        cmd2 = Mock(spec=Command)
        cmd2.hidden = False
        cmd2.get_short_help_str = Mock(return_value="Help for command 2")
        
        # Mock list_commands to return subcommands
        group.list_commands = Mock(return_value=["cmd1", "cmd2"])
        # Mock get_command to return the commands
        group.get_command = Mock(side_effect=[cmd1, cmd2])
        
        # Mock formatter section context manager
        section_mock = MagicMock()
        formatter.section.return_value.__enter__ = Mock(return_value=None)
        formatter.section.return_value.__exit__ = Mock(return_value=None)
        
        # Set formatter width for limit calculation
        formatter.width = 80
        
        group.format_commands(ctx, formatter)
        
        # Verify section was created and write_dl was called
        formatter.section.assert_called_once()
        formatter.write_dl.assert_called_once()
        
        # Verify the rows passed to write_dl
        args, _ = formatter.write_dl.call_args
        rows = args[0]
        assert len(rows) == 2
        assert rows[0] == ("cmd1", "Help for command 1")
        assert rows[1] == ("cmd2", "Help for command 2")
    
    def test_format_commands_limit_calculation(self):
        """Test the limit calculation for short help strings."""
        group = Group("test_group")
        ctx = Mock(spec=Context)
        formatter = Mock(spec=HelpFormatter)
        
        # Create a command with a long name to test limit calculation
        cmd = Mock(spec=Command)
        cmd.hidden = False
        cmd.get_short_help_str = Mock(return_value="Short help")
        
        # Mock list_commands to return a subcommand with long name
        group.list_commands = Mock(return_value=["very_long_command_name"])
        group.get_command = Mock(return_value=cmd)
        
        # Mock formatter section context manager
        formatter.section.return_value.__enter__ = Mock(return_value=None)
        formatter.section.return_value.__exit__ = Mock(return_value=None)
        
        # Set formatter width
        formatter.width = 80
        
        group.format_commands(ctx, formatter)
        
        # Verify get_short_help_str was called with calculated limit
        cmd.get_short_help_str.assert_called_once()
        call_args = cmd.get_short_help_str.call_args[0]
        assert len(call_args) == 1
        limit = call_args[0]
        
        # Verify limit calculation: width - 6 - max command name length
        max_cmd_length = len("very_long_command_name")
        expected_limit = 80 - 6 - max_cmd_length
        assert limit == expected_limit
    
    def test_format_commands_mixed_scenario(self):
        """Test a mixed scenario with None, hidden, and valid commands."""
        group = Group("test_group")
        ctx = Mock(spec=Context)
        formatter = Mock(spec=HelpFormatter)
        
        # Create commands with different scenarios
        cmd1 = Mock(spec=Command)  # Valid command
        cmd1.hidden = False
        cmd1.get_short_help_str = Mock(return_value="Valid command help")
        
        cmd2 = Mock(spec=Command)  # Hidden command
        cmd2.hidden = True
        
        # Mock list_commands to return mixed subcommands
        group.list_commands = Mock(return_value=["valid_cmd", "hidden_cmd", "nonexistent_cmd"])
        # Mock get_command to return different values
        group.get_command = Mock(side_effect=[cmd1, cmd2, None])
        
        # Mock formatter section context manager
        formatter.section.return_value.__enter__ = Mock(return_value=None)
        formatter.section.return_value.__exit__ = Mock(return_value=None)
        
        # Set formatter width
        formatter.width = 80
        
        group.format_commands(ctx, formatter)
        
        # Verify only the valid command was processed
        formatter.section.assert_called_once()
        formatter.write_dl.assert_called_once()
        
        # Verify only one row was written (the valid command)
        args, _ = formatter.write_dl.call_args
        rows = args[0]
        assert len(rows) == 1
        assert rows[0] == ("valid_cmd", "Valid command help")
