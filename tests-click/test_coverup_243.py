# file: src/click/src/click/core.py:1977-1985
# asked: {"lines": [1977, 1979, 1980, 1983, 1985], "branches": []}
# gained: {"lines": [1977, 1979, 1980, 1983, 1985], "branches": []}

import pytest
import click
from click.core import CommandCollection, Group, Context

class TestCommandCollection:
    def test_init_with_name_and_sources(self):
        """Test CommandCollection initialization with name and sources parameters."""
        # Create mock groups to use as sources
        source1 = Group("source1")
        source2 = Group("source2")
        sources = [source1, source2]
        
        # Initialize CommandCollection with name and sources
        cmd_collection = CommandCollection(name="test_collection", sources=sources)
        
        # Verify the name is set correctly
        assert cmd_collection.name == "test_collection"
        # Verify sources are stored correctly
        assert cmd_collection.sources == sources
        # Verify sources is the same list object (not a copy)
        assert cmd_collection.sources is sources

    def test_init_with_name_only(self):
        """Test CommandCollection initialization with name only (no sources)."""
        # Initialize CommandCollection with name but no sources
        cmd_collection = CommandCollection(name="test_collection")
        
        # Verify the name is set correctly
        assert cmd_collection.name == "test_collection"
        # Verify sources defaults to empty list
        assert cmd_collection.sources == []

    def test_init_with_sources_only(self):
        """Test CommandCollection initialization with sources only (no name)."""
        # Create mock groups to use as sources
        source1 = Group("source1")
        source2 = Group("source2")
        sources = [source1, source2]
        
        # Initialize CommandCollection with sources but no name
        cmd_collection = CommandCollection(sources=sources)
        
        # Verify name is None (default from Group)
        assert cmd_collection.name is None
        # Verify sources are stored correctly
        assert cmd_collection.sources == sources

    def test_init_with_no_parameters(self):
        """Test CommandCollection initialization with no parameters."""
        # Initialize CommandCollection with no parameters
        cmd_collection = CommandCollection()
        
        # Verify name is None (default from Group)
        assert cmd_collection.name is None
        # Verify sources defaults to empty list
        assert cmd_collection.sources == []

    def test_init_with_none_sources(self):
        """Test CommandCollection initialization with explicit None sources."""
        # Initialize CommandCollection with explicit None for sources
        cmd_collection = CommandCollection(name="test_collection", sources=None)
        
        # Verify the name is set correctly
        assert cmd_collection.name == "test_collection"
        # Verify sources defaults to empty list when None is provided
        assert cmd_collection.sources == []

    def test_init_with_additional_kwargs(self):
        """Test CommandCollection initialization with additional kwargs passed to Group."""
        # Initialize CommandCollection with additional kwargs
        cmd_collection = CommandCollection(
            name="test_collection", 
            sources=None,
            help="Test help text"
        )
        
        # Verify the name is set correctly
        assert cmd_collection.name == "test_collection"
        # Verify sources defaults to empty list
        assert cmd_collection.sources == []
        # Verify additional kwargs are passed to parent Group
        assert cmd_collection.help == "Test help text"
