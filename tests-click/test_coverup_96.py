# file: src/click/src/click/core.py:1991-2006
# asked: {"lines": [1991, 1992, 1994, 1995, 1997, 1998, 2000, 2001, 2002, 2004, 2006], "branches": [[1994, 1995], [1994, 1997], [1997, 1998], [1997, 2006], [2000, 1997], [2000, 2001], [2001, 2002], [2001, 2004]]}
# gained: {"lines": [1991, 1992, 1994, 1995, 1997, 1998, 2000, 2001, 2002, 2004, 2006], "branches": [[1994, 1995], [1994, 1997], [1997, 1998], [1997, 2006], [2000, 1997], [2000, 2001], [2001, 2002], [2001, 2004]]}

import pytest
import click
from click.testing import CliRunner


class TestCommandCollectionGetCommand:
    """Test cases for CommandCollection.get_command method to achieve full coverage."""
    
    def test_get_command_found_in_parent(self):
        """Test when command is found in parent Group."""
        # Create a CommandCollection with a command in the parent group
        collection = click.CommandCollection(sources=[], name='collection')
        
        @click.command()
        def test_cmd():
            pass
        
        collection.add_command(test_cmd, name='test_cmd')
        
        ctx = click.Context(collection)
        result = collection.get_command(ctx, 'test_cmd')
        
        assert result is not None
        assert result.name == 'test'
    
    def test_get_command_found_in_source(self):
        """Test when command is found in one of the sources."""
        # Create a source group with a command
        source_group = click.Group('source_group')
        
        @click.command()
        def source_cmd():
            pass
        
        source_group.add_command(source_cmd, name='source_cmd')
        
        collection = click.CommandCollection(sources=[source_group], name='collection')
        
        ctx = click.Context(collection)
        result = collection.get_command(ctx, 'source_cmd')
        
        assert result is not None
        assert result.name == 'source'
    
    def test_get_command_found_in_source_with_chain_false(self):
        """Test when command is found in source and chain is False."""
        # Create a source group with a command
        source_group = click.Group('source_group')
        
        @click.command()
        def source_cmd():
            pass
        
        source_group.add_command(source_cmd, name='source_cmd')
        
        collection = click.CommandCollection(sources=[source_group], name='collection', chain=False)
        
        ctx = click.Context(collection)
        result = collection.get_command(ctx, 'source_cmd')
        
        assert result is not None
        assert result.name == 'source'
    
    def test_get_command_found_in_source_with_chain_true_and_group_command(self):
        """Test when command is found in source, chain is True, and command is a Group."""
        # Create a source group with a nested group
        source_group = click.Group('source_group')
        nested_group = click.Group('nested_group')
        
        @click.command()
        def nested_cmd():
            pass
        
        nested_group.add_command(nested_cmd, name='nested_cmd')
        source_group.add_command(nested_group, name='nested_group')
        
        collection = click.CommandCollection(sources=[source_group], name='collection', chain=True)
        
        ctx = click.Context(collection)
        
        # This should raise RuntimeError due to _check_nested_chain
        with pytest.raises(RuntimeError, match="Found the group 'nested_group' as subcommand to another group  'collection' that is in chain mode"):
            collection.get_command(ctx, 'nested_group')
    
    def test_get_command_not_found_anywhere(self):
        """Test when command is not found in parent or any source."""
        # Create a CommandCollection with no commands
        source_group = click.Group('source_group')
        
        collection = click.CommandCollection(sources=[source_group], name='collection')
        
        ctx = click.Context(collection)
        result = collection.get_command(ctx, 'nonexistent_cmd')
        
        assert result is None
    
    def test_get_command_found_in_second_source(self):
        """Test when command is found in the second source after first source doesn't have it."""
        # Create two source groups
        source_group1 = click.Group('source_group1')
        source_group2 = click.Group('source_group2')
        
        @click.command()
        def cmd_in_second():
            pass
        
        source_group2.add_command(cmd_in_second, name='cmd_in_second')
        
        collection = click.CommandCollection(sources=[source_group1, source_group2], name='collection')
        
        ctx = click.Context(collection)
        result = collection.get_command(ctx, 'cmd_in_second')
        
        assert result is not None
        assert result.name == 'cmd-in-second'
