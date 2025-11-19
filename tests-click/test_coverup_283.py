# file: src/click/src/click/core.py:1934-1951
# asked: {"lines": [1934, 1944, 1946, 1947, 1948, 1950, 1951], "branches": []}
# gained: {"lines": [1934, 1944, 1946, 1947, 1948, 1950, 1951], "branches": []}

import pytest
from click.core import Group, Command, Context
from click.shell_completion import CompletionItem
from click.testing import CliRunner

class MockCommand(Command):
    def __init__(self, name, help_str=None, hidden=False):
        super().__init__(name)
        self._help_str = help_str
        self.hidden = hidden

    def get_short_help_str(self):
        return self._help_str or f"Help for {self.name}"

class TestGroupShellComplete:
    def test_shell_complete_with_visible_commands(self):
        """Test that shell_complete returns CompletionItems for visible commands."""
        group = Group("test_group")
        cmd1 = MockCommand("cmd1", "Help for cmd1")
        cmd2 = MockCommand("cmd2", "Help for cmd2")
        hidden_cmd = MockCommand("hidden_cmd", "Hidden command", hidden=True)
        
        group.add_command(cmd1)
        group.add_command(cmd2)
        group.add_command(hidden_cmd)

        runner = CliRunner()
        with runner.isolation():
            ctx = Context(group)
            results = group.shell_complete(ctx, "cmd")
            
            assert len(results) == 2
            names = [item.value for item in results]
            helps = [item.help for item in results]
            assert "cmd1" in names
            assert "cmd2" in names
            assert "hidden_cmd" not in names
            assert "Help for cmd1" in helps
            assert "Help for cmd2" in helps

    def test_shell_complete_with_empty_incomplete(self):
        """Test that shell_complete works with empty incomplete string."""
        group = Group("test_group")
        cmd1 = MockCommand("alpha", "Help for alpha")
        cmd2 = MockCommand("beta", "Help for beta")
        
        group.add_command(cmd1)
        group.add_command(cmd2)

        runner = CliRunner()
        with runner.isolation():
            ctx = Context(group)
            results = group.shell_complete(ctx, "")
            
            assert len(results) == 2
            names = [item.value for item in results]
            helps = [item.help for item in results]
            assert "alpha" in names
            assert "beta" in names
            assert "Help for alpha" in helps
            assert "Help for beta" in helps

    def test_shell_complete_with_no_matching_commands(self):
        """Test that shell_complete returns empty list when no commands match."""
        group = Group("test_group")
        cmd1 = MockCommand("alpha", "Help for alpha")
        cmd2 = MockCommand("beta", "Help for beta")
        
        group.add_command(cmd1)
        group.add_command(cmd2)

        runner = CliRunner()
        with runner.isolation():
            ctx = Context(group)
            results = group.shell_complete(ctx, "xyz")
            
            assert len(results) == 0

    def test_shell_complete_includes_parent_completions(self, monkeypatch):
        """Test that shell_complete extends results with parent completions."""
        group = Group("test_group")
        cmd1 = MockCommand("subcmd", "Help for subcmd")
        group.add_command(cmd1)

        # Mock the parent's shell_complete to return some options
        def mock_parent_shell_complete(self, ctx, incomplete):
            return [CompletionItem("--help", help="Show this message")]
        
        runner = CliRunner()
        with runner.isolation():
            ctx = Context(group)
            
            # Patch the parent's shell_complete method with the correct signature
            monkeypatch.setattr(Command, "shell_complete", mock_parent_shell_complete)
            
            results = group.shell_complete(ctx, "sub")
            
            # Should include both the subcommand and parent completions
            assert len(results) >= 1
            names = [item.value for item in results]
            assert "subcmd" in names
            assert "--help" in names

    def test_shell_complete_with_partial_match(self):
        """Test that shell_complete works with partial command name matches."""
        group = Group("test_group")
        cmd1 = MockCommand("start", "Start command")
        cmd2 = MockCommand("stop", "Stop command")
        cmd3 = MockCommand("status", "Status command")
        
        group.add_command(cmd1)
        group.add_command(cmd2)
        group.add_command(cmd3)

        runner = CliRunner()
        with runner.isolation():
            ctx = Context(group)
            results = group.shell_complete(ctx, "st")
            
            assert len(results) == 3
            names = [item.value for item in results]
            assert "start" in names
            assert "stop" in names
            assert "status" in names

    def test_shell_complete_with_exact_match(self):
        """Test that shell_complete works with exact command name matches."""
        group = Group("test_group")
        cmd1 = MockCommand("exact", "Exact command")
        cmd2 = MockCommand("other", "Other command")
        
        group.add_command(cmd1)
        group.add_command(cmd2)

        runner = CliRunner()
        with runner.isolation():
            ctx = Context(group)
            results = group.shell_complete(ctx, "exact")
            
            assert len(results) == 1
            assert results[0].value == "exact"
            assert results[0].help == "Exact command"
