# file: src/click/src/click/types.py:145-160
# asked: {"lines": [145, 160], "branches": []}
# gained: {"lines": [145, 160], "branches": []}

import pytest
from click.core import Context, Command, Option
from click.shell_completion import CompletionItem
from click.types import ParamType

def test_paramtype_shell_complete_returns_empty_list():
    """Test that ParamType.shell_complete returns an empty list by default."""
    # Arrange
    param_type = ParamType()
    ctx = Context(Command("test_command"))
    param = Option(["--test-param"])
    incomplete = "test"
    
    # Act
    result = param_type.shell_complete(ctx, param, incomplete)
    
    # Assert
    assert result == []

def test_paramtype_shell_complete_with_empty_incomplete():
    """Test that ParamType.shell_complete works with empty incomplete string."""
    # Arrange
    param_type = ParamType()
    ctx = Context(Command("test_command"))
    param = Option(["--test-param"])
    incomplete = ""
    
    # Act
    result = param_type.shell_complete(ctx, param, incomplete)
    
    # Assert
    assert result == []

def test_paramtype_shell_complete_with_none_context_and_param():
    """Test that ParamType.shell_complete handles None context and parameter gracefully."""
    # Arrange
    param_type = ParamType()
    ctx = None
    param = None
    incomplete = "test"
    
    # Act
    result = param_type.shell_complete(ctx, param, incomplete)
    
    # Assert
    assert result == []
