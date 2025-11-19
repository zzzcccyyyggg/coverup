# file: src/click/src/click/shell_completion.py:347-357
# asked: {"lines": [347, 348, 349, 350, 352, 353, 354, 355, 357], "branches": []}
# gained: {"lines": [347, 348, 349, 350, 352, 353, 354, 355, 357], "branches": []}

import os
import pytest
from click.shell_completion import BashComplete, split_arg_string
from click import Command


class MockCommand(Command):
    """Mock command for testing."""
    def __init__(self):
        super().__init__('test_command')


class TestBashComplete:
    def test_get_completion_args_normal_case(self, monkeypatch):
        """Test get_completion_args with normal case where COMP_WORDS and COMP_CWORD are set."""
        monkeypatch.setenv("COMP_WORDS", "click command --option value incomplete")
        monkeypatch.setenv("COMP_CWORD", "4")
        
        complete = BashComplete(
            cli=MockCommand(),
            ctx_args={},
            prog_name="test_prog",
            complete_var="_TEST_COMPLETE"
        )
        args, incomplete = complete.get_completion_args()
        
        expected_args = ["command", "--option", "value"]
        assert args == expected_args
        assert incomplete == "incomplete"

    def test_get_completion_args_empty_incomplete(self, monkeypatch):
        """Test get_completion_args when incomplete word is empty string."""
        monkeypatch.setenv("COMP_WORDS", "click command --option")
        monkeypatch.setenv("COMP_CWORD", "3")
        
        complete = BashComplete(
            cli=MockCommand(),
            ctx_args={},
            prog_name="test_prog",
            complete_var="_TEST_COMPLETE"
        )
        args, incomplete = complete.get_completion_args()
        
        expected_args = ["command", "--option"]
        assert args == expected_args
        assert incomplete == ""

    def test_get_completion_args_index_error(self, monkeypatch):
        """Test get_completion_args when IndexError occurs getting incomplete word."""
        monkeypatch.setenv("COMP_WORDS", "click command")
        monkeypatch.setenv("COMP_CWORD", "2")
        
        complete = BashComplete(
            cli=MockCommand(),
            ctx_args={},
            prog_name="test_prog",
            complete_var="_TEST_COMPLETE"
        )
        args, incomplete = complete.get_completion_args()
        
        expected_args = ["command"]
        assert args == expected_args
        assert incomplete == ""

    def test_get_completion_args_single_word(self, monkeypatch):
        """Test get_completion_args with only one word (the command name)."""
        monkeypatch.setenv("COMP_WORDS", "click")
        monkeypatch.setenv("COMP_CWORD", "1")
        
        complete = BashComplete(
            cli=MockCommand(),
            ctx_args={},
            prog_name="test_prog",
            complete_var="_TEST_COMPLETE"
        )
        args, incomplete = complete.get_completion_args()
        
        assert args == []
        assert incomplete == ""

    def test_get_completion_args_with_quoted_args(self, monkeypatch):
        """Test get_completion_args with quoted arguments in COMP_WORDS."""
        monkeypatch.setenv("COMP_WORDS", 'click command "file with spaces" incomplete')
        monkeypatch.setenv("COMP_CWORD", "3")
        
        complete = BashComplete(
            cli=MockCommand(),
            ctx_args={},
            prog_name="test_prog",
            complete_var="_TEST_COMPLETE"
        )
        args, incomplete = complete.get_completion_args()
        
        expected_args = ["command", "file with spaces"]
        assert args == expected_args
        assert incomplete == "incomplete"
