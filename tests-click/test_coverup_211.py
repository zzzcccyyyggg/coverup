# file: src/click/src/click/core.py:455-474
# asked: {"lines": [455, 467, 468, 469, 470, 471, 472, 473], "branches": []}
# gained: {"lines": [455, 467, 468, 469, 470, 471, 472, 473], "branches": []}

import pytest
import click
from click.core import Context, Command


class TestCommand(Command):
    """A test command that implements to_info_dict for testing."""
    
    def to_info_dict(self, ctx):
        return {
            "name": self.name,
            "params": [param.name for param in self.params] if self.params else [],
            "help": self.help
        }


class TestContextToInfoDict:
    """Test cases for Context.to_info_dict method."""
    
    def test_to_info_dict_returns_expected_structure(self):
        """Test that to_info_dict returns the expected dictionary structure."""
        # Create a test command
        cmd = TestCommand(name="test_command", help="A test command")
        
        # Create a context with the command
        ctx = Context(
            command=cmd,
            info_name="test_info",
            allow_extra_args=True,
            allow_interspersed_args=False,
            ignore_unknown_options=True,
            auto_envvar_prefix="TEST_PREFIX"
        )
        
        # Call to_info_dict
        result = ctx.to_info_dict()
        
        # Verify the structure contains all expected keys
        expected_keys = {
            "command",
            "info_name", 
            "allow_extra_args",
            "allow_interspersed_args", 
            "ignore_unknown_options",
            "auto_envvar_prefix"
        }
        assert set(result.keys()) == expected_keys
        
        # Verify the values match the context's attributes
        assert result["info_name"] == ctx.info_name
        assert result["allow_extra_args"] == ctx.allow_extra_args
        assert result["allow_interspersed_args"] == ctx.allow_interspersed_args
        assert result["ignore_unknown_options"] == ctx.ignore_unknown_options
        assert result["auto_envvar_prefix"] == ctx.auto_envvar_prefix
        
        # Verify command info was populated by calling command's to_info_dict
        assert result["command"] == cmd.to_info_dict(ctx)
    
    def test_to_info_dict_with_none_values(self):
        """Test to_info_dict when some context attributes are None."""
        # Create a test command
        cmd = TestCommand(name="test_command")
        
        # Create a context with None values for some attributes
        # Note: allow_extra_args, allow_interspersed_args, and ignore_unknown_options
        # will default to the command's values if None is passed
        ctx = Context(
            command=cmd,
            info_name=None,
            auto_envvar_prefix=None
        )
        
        # Call to_info_dict
        result = ctx.to_info_dict()
        
        # Verify all keys are present
        expected_keys = {
            "command",
            "info_name", 
            "allow_extra_args",
            "allow_interspersed_args", 
            "ignore_unknown_options",
            "auto_envvar_prefix"
        }
        assert set(result.keys()) == expected_keys
        
        # Verify None values are preserved for attributes that can be None
        assert result["info_name"] is None
        assert result["auto_envvar_prefix"] is None
        
        # Verify boolean attributes use command defaults when None is passed
        assert result["allow_extra_args"] == cmd.allow_extra_args
        assert result["allow_interspersed_args"] == cmd.allow_interspersed_args
        assert result["ignore_unknown_options"] == cmd.ignore_unknown_options
        
        # Command info should still be populated
        assert result["command"] == cmd.to_info_dict(ctx)
    
    def test_to_info_dict_with_false_values(self):
        """Test to_info_dict with boolean False values."""
        # Create a test command with default boolean values
        cmd = TestCommand(name="test_command")
        
        # Create a context with explicit False values
        ctx = Context(
            command=cmd,
            info_name="test",
            allow_extra_args=False,
            allow_interspersed_args=False,
            ignore_unknown_options=False,
            auto_envvar_prefix=""
        )
        
        # Call to_info_dict
        result = ctx.to_info_dict()
        
        # Verify boolean False values are preserved
        assert result["allow_extra_args"] is False
        assert result["allow_interspersed_args"] is False
        assert result["ignore_unknown_options"] is False
        assert result["auto_envvar_prefix"] == ""
        
        # Verify other values
        assert result["info_name"] == "test"
        assert result["command"] == cmd.to_info_dict(ctx)
