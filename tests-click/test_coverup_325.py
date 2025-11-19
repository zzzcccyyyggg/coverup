# file: src/click/src/click/core.py:1987-1989
# asked: {"lines": [1987, 1989], "branches": []}
# gained: {"lines": [1987, 1989], "branches": []}

import pytest
import click


class TestCommandCollection:
    def test_add_source_adds_group_to_sources(self):
        """Test that add_source correctly adds a group to the sources list."""
        # Create a CommandCollection with no initial sources
        collection = click.CommandCollection(name="test_collection", sources=None)
        
        # Verify initial state
        assert collection.sources == []
        
        # Create a mock group to add
        group = click.Group(name="test_group")
        
        # Call add_source
        collection.add_source(group)
        
        # Verify the group was added to sources
        assert collection.sources == [group]
        
        # Test adding another group
        group2 = click.Group(name="test_group2")
        collection.add_source(group2)
        
        # Verify both groups are in sources
        assert collection.sources == [group, group2]
