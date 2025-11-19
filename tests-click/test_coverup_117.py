# file: src/click/src/click/core.py:54-70
# asked: {"lines": [54, 63, 65, 66, 67, 69, 70], "branches": [[65, 0], [65, 66], [66, 65], [66, 67], [69, 65], [69, 70]]}
# gained: {"lines": [54, 63, 65, 66, 67, 69, 70], "branches": [[65, 0], [65, 66], [66, 65], [66, 67], [69, 65], [69, 70]]}

import pytest
import click
from click.core import Context, Group, Command

class MockCommand(Command):
    """Mock command for testing."""
    def __init__(self, name, hidden=False):
        super().__init__(name)
        self.hidden = hidden

class MockGroup(Group):
    """Mock group for testing _complete_visible_commands."""
    def __init__(self, name, commands=None):
        super().__init__(name)
        if commands:
            for cmd_name, cmd in commands.items():
                self.add_command(cmd, cmd_name)
    
    def list_commands(self, ctx):
        return list(self.commands.keys())
    
    def get_command(self, ctx, name):
        return self.commands.get(name)

def test_complete_visible_commands_with_matching_incomplete():
    """Test _complete_visible_commands with incomplete string that matches some commands."""
    # Create a group with multiple commands
    cmd1 = MockCommand("start", hidden=False)
    cmd2 = MockCommand("stop", hidden=False) 
    cmd3 = MockCommand("status", hidden=False)
    cmd4 = MockCommand("hidden_cmd", hidden=True)
    
    group = MockGroup("test_group", {
        "start": cmd1,
        "stop": cmd2,
        "status": cmd3,
        "hidden_cmd": cmd4
    })
    
    ctx = Context(group)
    
    # Test with incomplete "st" - should match "start", "stop", "status" but not "hidden_cmd"
    result = list(click.core._complete_visible_commands(ctx, "st"))
    
    # Verify we get the expected commands
    expected = [("start", cmd1), ("stop", cmd2), ("status", cmd3)]
    assert len(result) == 3
    assert set(result) == set(expected)
    
    # Verify hidden command is not included
    assert ("hidden_cmd", cmd4) not in result

def test_complete_visible_commands_with_empty_incomplete():
    """Test _complete_visible_commands with empty incomplete string."""
    # Create a group with multiple commands
    cmd1 = MockCommand("alpha", hidden=False)
    cmd2 = MockCommand("beta", hidden=False)
    cmd3 = MockCommand("gamma", hidden=True)
    
    group = MockGroup("test_group", {
        "alpha": cmd1,
        "beta": cmd2,
        "gamma": cmd3
    })
    
    ctx = Context(group)
    
    # Test with empty incomplete - should return all non-hidden commands
    result = list(click.core._complete_visible_commands(ctx, ""))
    
    # Verify we get all non-hidden commands
    expected = [("alpha", cmd1), ("beta", cmd2)]
    assert len(result) == 2
    assert set(result) == set(expected)
    
    # Verify hidden command is not included
    assert ("gamma", cmd3) not in result

def test_complete_visible_commands_with_no_matches():
    """Test _complete_visible_commands with incomplete string that matches no commands."""
    # Create a group with commands
    cmd1 = MockCommand("foo", hidden=False)
    cmd2 = MockCommand("bar", hidden=False)
    
    group = MockGroup("test_group", {
        "foo": cmd1,
        "bar": cmd2
    })
    
    ctx = Context(group)
    
    # Test with incomplete "xyz" - should match nothing
    result = list(click.core._complete_visible_commands(ctx, "xyz"))
    
    # Verify no results
    assert len(result) == 0

def test_complete_visible_commands_with_partial_matches():
    """Test _complete_visible_commands with partial matches and hidden commands."""
    # Create a group with mixed hidden/visible commands
    cmd1 = MockCommand("visible1", hidden=False)
    cmd2 = MockCommand("visible2", hidden=False)
    cmd3 = MockCommand("hidden1", hidden=True)
    cmd4 = MockCommand("hidden2", hidden=True)
    
    group = MockGroup("test_group", {
        "visible1": cmd1,
        "visible2": cmd2,
        "hidden1": cmd3,
        "hidden2": cmd4
    })
    
    ctx = Context(group)
    
    # Test with incomplete "vis" - should match only visible commands
    result = list(click.core._complete_visible_commands(ctx, "vis"))
    
    # Verify we get only visible commands that match
    expected = [("visible1", cmd1), ("visible2", cmd2)]
    assert len(result) == 2
    assert set(result) == set(expected)
    
    # Verify hidden commands are not included even if they match
    assert ("hidden1", cmd3) not in result
    assert ("hidden2", cmd4) not in result

def test_complete_visible_commands_with_none_command():
    """Test _complete_visible_commands when get_command returns None."""
    class MockGroupWithNone(Group):
        def __init__(self, name):
            super().__init__(name)
            self.commands = {"existing": MockCommand("existing")}
        
        def list_commands(self, ctx):
            return ["existing", "nonexistent"]
        
        def get_command(self, ctx, name):
            if name == "nonexistent":
                return None
            return self.commands.get(name)
    
    group = MockGroupWithNone("test_group")
    ctx = Context(group)
    
    # Test with empty incomplete - should only return the existing command
    result = list(click.core._complete_visible_commands(ctx, ""))
    
    # Verify we only get the existing command, not the nonexistent one
    assert len(result) == 1
    assert result[0][0] == "existing"
