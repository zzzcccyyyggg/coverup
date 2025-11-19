# file: src/click/src/click/core.py:2008-2014
# asked: {"lines": [2008, 2009, 2011, 2012, 2014], "branches": [[2011, 2012], [2011, 2014]]}
# gained: {"lines": [2008, 2009, 2011, 2012, 2014], "branches": [[2011, 2012], [2011, 2014]]}

import pytest
import click
from click.core import Context, CommandCollection, Group

class MockGroup(Group):
    """A mock Group for testing CommandCollection's list_commands method."""
    def __init__(self, name=None, commands=None):
        super().__init__(name=name, commands=commands or {})
    
    def list_commands(self, ctx):
        return sorted(self.commands.keys())

def test_command_collection_list_commands_with_sources():
    """Test CommandCollection.list_commands with multiple sources."""
    # Create a context
    ctx = Context(click.Command('test'))
    
    # Create source groups with commands
    source1 = MockGroup('source1', {'cmd1': click.Command('cmd1'), 'cmd3': click.Command('cmd3')})
    source2 = MockGroup('source2', {'cmd2': click.Command('cmd2'), 'cmd4': click.Command('cmd4')})
    
    # Create CommandCollection with sources
    collection = CommandCollection('collection', sources=[source1, source2])
    
    # Add some commands directly to the collection
    collection.add_command(click.Command('cmd0'))
    
    # Test list_commands - should include commands from collection and all sources
    result = collection.list_commands(ctx)
    
    # Verify all commands are present and sorted
    expected = ['cmd0', 'cmd1', 'cmd2', 'cmd3', 'cmd4']
    assert result == expected

def test_command_collection_list_commands_empty_sources():
    """Test CommandCollection.list_commands with empty sources list."""
    # Create a context
    ctx = Context(click.Command('test'))
    
    # Create CommandCollection with no sources
    collection = CommandCollection('collection', sources=[])
    
    # Add some commands directly to the collection
    collection.add_command(click.Command('cmd1'))
    collection.add_command(click.Command('cmd2'))
    
    # Test list_commands - should only include commands from collection itself
    result = collection.list_commands(ctx)
    
    # Verify only collection commands are present
    expected = ['cmd1', 'cmd2']
    assert result == expected

def test_command_collection_list_commands_no_commands():
    """Test CommandCollection.list_commands with no commands in collection or sources."""
    # Create a context
    ctx = Context(click.Command('test'))
    
    # Create empty source groups
    source1 = MockGroup('source1', {})
    source2 = MockGroup('source2', {})
    
    # Create CommandCollection with empty sources and no commands
    collection = CommandCollection('collection', sources=[source1, source2])
    
    # Test list_commands - should return empty sorted list
    result = collection.list_commands(ctx)
    
    # Verify empty result
    assert result == []
