# file: src/click/src/click/core.py:826-843
# asked: {"lines": [826, 836, 837, 839, 840, 841, 843], "branches": [[836, 837], [836, 839], [839, 840], [839, 843], [840, 839], [840, 841]]}
# gained: {"lines": [826, 836, 837, 839, 840, 841, 843], "branches": [[836, 837], [836, 839], [839, 840], [839, 843], [840, 839], [840, 841]]}

import pytest
import click
from click.core import Context, Command

class MockCommand(Command):
    """A mock command for testing."""
    def __init__(self, name="test_cmd"):
        super().__init__(name=name)
    
    def invoke(self, ctx):
        return f"invoked {self.name}"

class MockCallback:
    """A mock callback that is not a Command."""
    def __call__(self, *args, **kwargs):
        return "callback result"

def test_forward_with_non_command_raises_type_error():
    """Test that forward raises TypeError when called with a non-Command callback."""
    ctx = Context(Command("parent"))
    
    with pytest.raises(TypeError, match="Callback is not a command."):
        ctx.forward(MockCallback())

def test_forward_with_command_and_params():
    """Test that forward properly forwards params from context to the command."""
    parent_cmd = Command("parent")
    ctx = Context(parent_cmd)
    
    # Set some params in the context
    ctx.params = {"param1": "value1", "param2": "value2"}
    
    child_cmd = MockCommand("child")
    
    # Mock the invoke method to capture the kwargs
    def mock_invoke(cmd, *args, **kwargs):
        assert cmd == child_cmd
        # Check that params from context are forwarded
        assert kwargs["param1"] == "value1"
        assert kwargs["param2"] == "value2"
        return "invoked with forwarded params"
    
    ctx.invoke = mock_invoke
    
    result = ctx.forward(child_cmd)
    assert result == "invoked with forwarded params"

def test_forward_with_command_and_explicit_kwargs():
    """Test that explicit kwargs override context params in forward."""
    parent_cmd = Command("parent")
    ctx = Context(parent_cmd)
    
    # Set some params in the context
    ctx.params = {"param1": "value1", "param2": "value2"}
    
    child_cmd = MockCommand("child")
    
    # Mock the invoke method to capture the kwargs
    def mock_invoke(cmd, *args, **kwargs):
        assert cmd == child_cmd
        # Check that explicit kwargs override context params
        assert kwargs["param1"] == "explicit_value"  # overridden
        assert kwargs["param2"] == "value2"  # from context
        return "invoked with mixed params"
    
    ctx.invoke = mock_invoke
    
    result = ctx.forward(child_cmd, param1="explicit_value")
    assert result == "invoked with mixed params"

def test_forward_with_command_and_args():
    """Test that forward properly passes args to the command."""
    parent_cmd = Command("parent")
    ctx = Context(parent_cmd)
    
    child_cmd = MockCommand("child")
    
    # Mock the invoke method to capture the args
    def mock_invoke(cmd, *args, **kwargs):
        assert cmd == child_cmd
        assert args == ("arg1", "arg2")
        return "invoked with args"
    
    ctx.invoke = mock_invoke
    
    result = ctx.forward(child_cmd, "arg1", "arg2")
    assert result == "invoked with args"

def test_forward_with_empty_context_params():
    """Test forward when context has no params."""
    parent_cmd = Command("parent")
    ctx = Context(parent_cmd)
    ctx.params = {}  # Empty params
    
    child_cmd = MockCommand("child")
    
    # Mock the invoke method
    def mock_invoke(cmd, *args, **kwargs):
        assert cmd == child_cmd
        assert kwargs == {}  # No params forwarded
        return "invoked with no params"
    
    ctx.invoke = mock_invoke
    
    result = ctx.forward(child_cmd)
    assert result == "invoked with no params"
