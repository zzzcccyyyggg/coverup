# file: src/click/src/click/core.py:1054-1079
# asked: {"lines": [1054, 1062, 1064, 1065, 1071, 1073, 1076, 1077, 1079], "branches": [[1064, 1065], [1064, 1071], [1071, 1073], [1071, 1079]]}
# gained: {"lines": [1054, 1062, 1064, 1065, 1071, 1073, 1076, 1077, 1079], "branches": [[1064, 1065], [1064, 1071], [1071, 1073], [1071, 1079]]}

import pytest
import click
from click.core import Command, Context


class TestCommandGetHelpOption:
    """Test cases for Command.get_help_option method to achieve full coverage."""
    
    def test_get_help_option_returns_none_when_no_help_option_names(self):
        """Test that get_help_option returns None when help_option_names is empty."""
        cmd = Command(name="test_cmd")
        ctx = Context(cmd)
        
        # Mock get_help_option_names to return empty list
        cmd.get_help_option_names = lambda ctx: []
        
        result = cmd.get_help_option(ctx)
        assert result is None
    
    def test_get_help_option_returns_none_when_add_help_option_false(self):
        """Test that get_help_option returns None when add_help_option is False."""
        cmd = Command(name="test_cmd", add_help_option=False)
        ctx = Context(cmd)
        
        # Mock get_help_option_names to return some names
        cmd.get_help_option_names = lambda ctx: ["--help"]
        
        result = cmd.get_help_option(ctx)
        assert result is None
    
    def test_get_help_option_creates_and_caches_help_option(self):
        """Test that get_help_option creates and caches the help option on first call."""
        cmd = Command(name="test_cmd")
        ctx = Context(cmd)
        
        # Mock get_help_option_names to return help option names
        cmd.get_help_option_names = lambda ctx: ["--help"]
        
        # Ensure _help_option is None initially
        assert cmd._help_option is None
        
        # First call should create and cache the help option
        result1 = cmd.get_help_option(ctx)
        assert result1 is not None
        assert cmd._help_option is result1
        
        # Second call should return the cached option
        result2 = cmd.get_help_option(ctx)
        assert result2 is result1
    
    def test_get_help_option_uses_custom_help_option_names(self):
        """Test that get_help_option uses custom help option names from context."""
        cmd = Command(name="test_cmd")
        
        # Create context with custom help option names
        ctx = Context(cmd, help_option_names=["-h", "--help"])
        
        # Mock get_help_option_names to return context's help option names
        cmd.get_help_option_names = lambda ctx: ctx.help_option_names
        
        result = cmd.get_help_option(ctx)
        assert result is not None
        assert cmd._help_option is result
    
    def test_get_help_option_with_parent_context_help_names(self):
        """Test that get_help_option inherits help option names from parent context."""
        parent_cmd = Command(name="parent_cmd")
        parent_ctx = Context(parent_cmd, help_option_names=["-h", "--help"])
        
        cmd = Command(name="child_cmd")
        ctx = Context(cmd, parent=parent_ctx)
        
        # Mock get_help_option_names to return context's help option names
        cmd.get_help_option_names = lambda ctx: ctx.help_option_names
        
        result = cmd.get_help_option(ctx)
        assert result is not None
        assert cmd._help_option is result
        assert ctx.help_option_names == ["-h", "--help"]
    
    def test_get_help_option_multiple_calls_same_context(self):
        """Test that multiple calls with same context return same cached option."""
        cmd = Command(name="test_cmd")
        ctx = Context(cmd)
        
        cmd.get_help_option_names = lambda ctx: ["--help"]
        
        # Call multiple times
        result1 = cmd.get_help_option(ctx)
        result2 = cmd.get_help_option(ctx)
        result3 = cmd.get_help_option(ctx)
        
        # All should be the same cached object
        assert result1 is result2
        assert result2 is result3
        assert cmd._help_option is result1
    
    def test_get_help_option_after_reset(self, monkeypatch):
        """Test that help option is recreated if _help_option is manually reset."""
        cmd = Command(name="test_cmd")
        ctx = Context(cmd)
        
        cmd.get_help_option_names = lambda ctx: ["--help"]
        
        # First call creates and caches
        result1 = cmd.get_help_option(ctx)
        assert cmd._help_option is result1
        
        # Manually reset _help_option
        cmd._help_option = None
        
        # Second call should recreate
        result2 = cmd.get_help_option(ctx)
        assert result2 is not None
        assert cmd._help_option is result2
        # Should be a different object since it was recreated
        assert result1 is not result2
