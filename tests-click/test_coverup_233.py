# file: src/click/src/click/shell_completion.py:224-234
# asked: {"lines": [224, 231, 232, 233, 234], "branches": []}
# gained: {"lines": [224, 231, 232, 233, 234], "branches": []}

import pytest
from click.core import Command
from click.shell_completion import ShellComplete
import collections.abc as cabc
from typing import Any, MutableMapping


class MockCommand(Command):
    def __init__(self, name: str = "test_command"):
        super().__init__(name)


class TestShellComplete:
    def test_shell_complete_init(self):
        """Test that ShellComplete.__init__ properly initializes all attributes."""
        # Arrange
        cli = MockCommand()
        ctx_args: MutableMapping[str, Any] = {"test": "value"}
        prog_name = "test_prog"
        complete_var = "_TEST_COMPLETE"
        
        # Act
        shell_complete = ShellComplete(
            cli=cli,
            ctx_args=ctx_args,
            prog_name=prog_name,
            complete_var=complete_var
        )
        
        # Assert
        assert shell_complete.cli == cli
        assert shell_complete.ctx_args == ctx_args
        assert shell_complete.prog_name == prog_name
        assert shell_complete.complete_var == complete_var

    def test_shell_complete_init_with_empty_ctx_args(self):
        """Test that ShellComplete.__init__ works with empty context arguments."""
        # Arrange
        cli = MockCommand()
        ctx_args: MutableMapping[str, Any] = {}
        prog_name = "test_prog"
        complete_var = "_TEST_COMPLETE"
        
        # Act
        shell_complete = ShellComplete(
            cli=cli,
            ctx_args=ctx_args,
            prog_name=prog_name,
            complete_var=complete_var
        )
        
        # Assert
        assert shell_complete.cli == cli
        assert shell_complete.ctx_args == ctx_args
        assert shell_complete.prog_name == prog_name
        assert shell_complete.complete_var == complete_var

    def test_shell_complete_init_with_none_values(self):
        """Test that ShellComplete.__init__ handles None values appropriately."""
        # Arrange
        cli = MockCommand()
        ctx_args: MutableMapping[str, Any] = {"key": None}
        prog_name = "test_prog"
        complete_var = "_TEST_COMPLETE"
        
        # Act
        shell_complete = ShellComplete(
            cli=cli,
            ctx_args=ctx_args,
            prog_name=prog_name,
            complete_var=complete_var
        )
        
        # Assert
        assert shell_complete.cli == cli
        assert shell_complete.ctx_args == ctx_args
        assert shell_complete.prog_name == prog_name
        assert shell_complete.complete_var == complete_var
