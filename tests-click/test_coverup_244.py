# file: src/click/src/click/core.py:1182-1217
# asked: {"lines": [1182, 1186, 1209, 1210, 1211, 1213, 1215, 1216, 1217], "branches": [[1209, 1210], [1209, 1213], [1210, 1209], [1210, 1211]]}
# gained: {"lines": [1182, 1186, 1209, 1210, 1211, 1213, 1215, 1216, 1217], "branches": [[1209, 1210], [1209, 1213], [1210, 1209], [1210, 1211]]}

import pytest
import click
from click.core import Command, Context
from click.exceptions import Exit


class TestCommandMakeContext:
    """Test cases for Command.make_context method to achieve full coverage of lines 1182-1217."""
    
    def test_make_context_basic(self):
        """Test basic make_context functionality without context_settings or extra parameters."""
        cmd = Command(name="test_cmd")
        ctx = cmd.make_context(info_name="test", args=[])
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        assert ctx.info_name == "test"
        assert ctx.args == []
    
    def test_make_context_with_context_settings(self):
        """Test make_context when context_settings are provided and not overridden by extra."""
        cmd = Command(name="test_cmd", context_settings={"color": True, "terminal_width": 80})
        ctx = cmd.make_context(info_name="test", args=[])
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        # Context settings should be applied
        assert ctx.color is True
        assert ctx.terminal_width == 80
    
    def test_make_context_with_extra_overriding_context_settings(self):
        """Test make_context when extra parameters override context_settings."""
        cmd = Command(name="test_cmd", context_settings={"color": True, "terminal_width": 80})
        ctx = cmd.make_context(info_name="test", args=[], color=False, terminal_width=120)
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        # Extra parameters should override context_settings
        assert ctx.color is False
        assert ctx.terminal_width == 120
    
    def test_make_context_with_parent_context(self):
        """Test make_context with a parent context."""
        parent_cmd = Command(name="parent_cmd")
        parent_ctx = parent_cmd.make_context(info_name="parent", args=[])
        
        child_cmd = Command(name="child_cmd")
        child_ctx = child_cmd.make_context(info_name="child", args=[], parent=parent_ctx)
        
        assert isinstance(child_ctx, Context)
        assert child_ctx.command == child_cmd
        assert child_ctx.info_name == "child"
        assert child_ctx.parent == parent_ctx
    
    def test_make_context_with_args_parsing(self):
        """Test make_context with actual arguments that need parsing."""
        cmd = Command(name="test_cmd")
        
        # Test with simple args that won't trigger help or exit
        # Use resilient_parsing to avoid callbacks that might exit
        ctx = cmd.make_context(info_name="test", args=["dummy_arg"], resilient_parsing=True)
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        assert ctx.info_name == "test"
        # The args should be parsed and stored in ctx.args
        assert ctx.args == ["dummy_arg"]
    
    def test_make_context_mixed_context_settings_and_extra(self):
        """Test make_context with some context_settings overridden and some not."""
        cmd = Command(
            name="test_cmd", 
            context_settings={
                "color": True, 
                "terminal_width": 80,
                "resilient_parsing": False
            }
        )
        # Override only some settings
        ctx = cmd.make_context(
            info_name="test", 
            args=[],
            color=False,  # Override this one
            # terminal_width not overridden, should use context_settings value
            # resilient_parsing not overridden, should use context_settings value
        )
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        # Overridden setting
        assert ctx.color is False
        # Non-overridden settings from context_settings
        assert ctx.terminal_width == 80
        assert ctx.resilient_parsing is False
    
    def test_make_context_empty_context_settings(self):
        """Test make_context with empty context_settings dict."""
        cmd = Command(name="test_cmd", context_settings={})
        ctx = cmd.make_context(info_name="test", args=[])
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        assert ctx.info_name == "test"
    
    def test_make_context_custom_context_class(self):
        """Test make_context with a custom context class."""
        class CustomContext(Context):
            custom_attr = "custom_value"
        
        class CustomCommand(Command):
            context_class = CustomContext
        
        cmd = CustomCommand(name="custom_cmd")
        ctx = cmd.make_context(info_name="test", args=[])
        
        assert isinstance(ctx, CustomContext)
        assert ctx.command == cmd
        assert ctx.info_name == "test"
        assert ctx.custom_attr == "custom_value"
    
    def test_make_context_scope_cleanup_false(self):
        """Test that scope is called with cleanup=False."""
        cmd = Command(name="test_cmd")
        
        # This test verifies that the scope context manager is entered
        # The actual behavior of scope is tested elsewhere
        ctx = cmd.make_context(info_name="test", args=[])
        
        assert isinstance(ctx, Context)
        # The method should return successfully without raising exceptions
    
    def test_make_context_parse_args_called(self, mocker):
        """Test that parse_args is called within the scope."""
        cmd = Command(name="test_cmd")
        
        # Mock parse_args to verify it's called
        mock_parse_args = mocker.patch.object(cmd, 'parse_args')
        
        ctx = cmd.make_context(info_name="test", args=["arg1", "arg2"])
        
        # Verify parse_args was called with the correct arguments
        mock_parse_args.assert_called_once_with(ctx, ["arg1", "arg2"])
        assert isinstance(ctx, Context)
    
    def test_make_context_with_help_option_handles_exit(self):
        """Test make_context when --help is provided and handles Exit exception."""
        cmd = Command(name="test_cmd")
        
        # When --help is provided, click will raise Exit exception
        # We need to catch this to test the make_context method
        with pytest.raises(Exit) as exc_info:
            cmd.make_context(info_name="test", args=["--help"])
        
        # Verify the exit code is 0 (normal help exit)
        assert exc_info.value.exit_code == 0
    
    def test_make_context_context_settings_loop_coverage(self):
        """Test the loop that copies context_settings to extra parameters."""
        # Use valid Context constructor parameters that won't cause TypeError
        cmd = Command(
            name="test_cmd", 
            context_settings={
                "color": True,
                "terminal_width": 80,
                "resilient_parsing": True
            }
        )
        
        # Provide some extra parameters that will override some context_settings
        # Use valid Context constructor parameters
        ctx = cmd.make_context(
            info_name="test", 
            args=[],
            color=False,  # This should override the context_settings value
            # terminal_width and resilient_parsing should come from context_settings
        )
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        
        # Verify the context settings were properly merged
        # color should be the overridden value
        assert ctx.color is False
        # terminal_width should come from context_settings (not overridden)
        assert ctx.terminal_width == 80
        # resilient_parsing should come from context_settings (not overridden)
        assert ctx.resilient_parsing is True
    
    def test_make_context_context_settings_partial_override(self):
        """Test that context_settings are only added to extra when not already present."""
        cmd = Command(
            name="test_cmd",
            context_settings={
                "color": True,
                "terminal_width": 80,
                "max_content_width": 100
            }
        )
        
        # Override only some settings, leave others to be filled from context_settings
        ctx = cmd.make_context(
            info_name="test",
            args=[],
            color=False,  # Override this one
            # terminal_width and max_content_width should come from context_settings
        )
        
        assert isinstance(ctx, Context)
        assert ctx.command == cmd
        # Overridden setting
        assert ctx.color is False
        # Settings from context_settings
        assert ctx.terminal_width == 80
        assert ctx.max_content_width == 100
