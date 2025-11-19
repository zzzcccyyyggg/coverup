# file: src/click/src/click/core.py:273-441
# asked: {"lines": [273, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 293, 295, 297, 300, 302, 307, 309, 311, 312, 315, 316, 319, 320, 321, 322, 323, 325, 327, 339, 341, 342, 345, 347, 348, 352, 354, 355, 361, 363, 364, 370, 372, 373, 383, 385, 386, 387, 389, 392, 394, 395, 399, 404, 409, 410, 411, 412, 413, 415, 416, 419, 421, 422, 424, 426, 427, 430, 432, 433, 436, 438, 439, 440, 441], "branches": [[311, 312], [311, 315], [319, 325], [319, 327], [341, 342], [341, 345], [347, 348], [347, 352], [354, 355], [354, 361], [363, 364], [363, 370], [372, 373], [372, 383], [385, 386], [385, 392], [386, 387], [386, 389], [394, 395], [394, 399], [409, 410], [409, 419], [410, 415], [410, 421], [421, 422], [421, 424], [426, 427], [426, 430], [432, 433], [432, 436]]}
# gained: {"lines": [273, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 293, 295, 297, 300, 302, 307, 309, 311, 312, 315, 316, 319, 320, 321, 322, 323, 325, 327, 339, 341, 342, 345, 347, 348, 352, 354, 355, 361, 363, 364, 370, 372, 373, 383, 385, 386, 387, 389, 392, 394, 395, 399, 404, 409, 410, 411, 412, 413, 415, 416, 419, 421, 422, 424, 426, 427, 430, 432, 433, 436, 438, 439, 440, 441], "branches": [[311, 312], [311, 315], [319, 325], [319, 327], [341, 342], [341, 345], [347, 348], [347, 352], [354, 355], [354, 361], [363, 364], [363, 370], [372, 373], [372, 383], [385, 386], [385, 392], [386, 387], [386, 389], [394, 395], [394, 399], [409, 410], [409, 419], [410, 415], [410, 421], [421, 422], [421, 424], [426, 427], [426, 430], [432, 433], [432, 436]]}

import pytest
import click
from click.core import Context, Command


class TestContextInit:
    """Test cases for Context.__init__ method to achieve full coverage."""
    
    def test_context_init_with_parent_and_default_map(self):
        """Test Context initialization with parent and default_map inheritance."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, info_name="parent")
        parent_ctx.default_map = {"child": {"param": "value"}}
        
        child_command = Command("child")
        child_ctx = Context(
            child_command, 
            parent=parent_ctx, 
            info_name="child"
        )
        
        assert child_ctx.parent == parent_ctx
        assert child_ctx.command == child_command
        assert child_ctx.info_name == "child"
        assert child_ctx.default_map == {"param": "value"}
        assert child_ctx.obj is None
        assert child_ctx._meta == {}
    
    def test_context_init_with_parent_obj_inheritance(self):
        """Test Context initialization with parent obj inheritance."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, obj="parent_object")
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx)
        
        assert child_ctx.obj == "parent_object"
    
    def test_context_init_with_parent_terminal_width_inheritance(self):
        """Test Context initialization with parent terminal_width inheritance."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, terminal_width=100)
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx)
        
        assert child_ctx.terminal_width == 100
    
    def test_context_init_with_parent_max_content_width_inheritance(self):
        """Test Context initialization with parent max_content_width inheritance."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, max_content_width=120)
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx)
        
        assert child_ctx.max_content_width == 120
    
    def test_context_init_with_command_allow_extra_args(self):
        """Test Context initialization with command's allow_extra_args."""
        command = Command("test")
        command.allow_extra_args = True
        
        ctx = Context(command)
        
        assert ctx.allow_extra_args is True
    
    def test_context_init_with_command_allow_interspersed_args(self):
        """Test Context initialization with command's allow_interspersed_args."""
        command = Command("test")
        command.allow_interspersed_args = False
        
        ctx = Context(command)
        
        assert ctx.allow_interspersed_args is False
    
    def test_context_init_with_command_ignore_unknown_options(self):
        """Test Context initialization with command's ignore_unknown_options."""
        command = Command("test")
        command.ignore_unknown_options = True
        
        ctx = Context(command)
        
        assert ctx.ignore_unknown_options is True
    
    def test_context_init_with_parent_help_option_names(self):
        """Test Context initialization with parent help_option_names."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, help_option_names=["--help", "-h"])
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx)
        
        assert child_ctx.help_option_names == ["--help", "-h"]
    
    def test_context_init_without_parent_help_option_names(self):
        """Test Context initialization without parent help_option_names."""
        command = Command("test")
        ctx = Context(command)
        
        assert ctx.help_option_names == ["--help"]
    
    def test_context_init_with_parent_token_normalize_func(self):
        """Test Context initialization with parent token_normalize_func."""
        def normalize_func(token):
            return token.lower()
        
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, token_normalize_func=normalize_func)
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx)
        
        assert child_ctx.token_normalize_func == normalize_func
    
    def test_context_init_with_auto_envvar_prefix_from_parent(self):
        """Test Context initialization with auto_envvar_prefix from parent."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, auto_envvar_prefix="PARENT")
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx, info_name="child")
        
        assert child_ctx.auto_envvar_prefix == "PARENT_CHILD"
    
    def test_context_init_with_auto_envvar_prefix_uppercase(self):
        """Test Context initialization with auto_envvar_prefix uppercase conversion."""
        command = Command("test")
        ctx = Context(command, auto_envvar_prefix="test-prefix")
        
        assert ctx.auto_envvar_prefix == "TEST_PREFIX"
    
    def test_context_init_with_parent_color_inheritance(self):
        """Test Context initialization with parent color inheritance."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, color=True)
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx)
        
        assert child_ctx.color is True
    
    def test_context_init_with_parent_show_default_inheritance(self):
        """Test Context initialization with parent show_default inheritance."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, show_default=True)
        
        child_command = Command("child")
        child_ctx = Context(child_command, parent=parent_ctx)
        
        assert child_ctx.show_default is True
    
    def test_context_init_with_resilient_parsing(self):
        """Test Context initialization with resilient_parsing enabled."""
        command = Command("test")
        ctx = Context(command, resilient_parsing=True)
        
        assert ctx.resilient_parsing is True
    
    def test_context_init_with_custom_default_map(self):
        """Test Context initialization with custom default_map."""
        command = Command("test")
        default_map = {"param1": "value1", "param2": "value2"}
        ctx = Context(command, default_map=default_map)
        
        assert ctx.default_map == default_map
    
    def test_context_init_with_all_parameters(self):
        """Test Context initialization with all parameters specified."""
        parent_command = Command("parent")
        parent_ctx = Context(parent_command, obj="parent_obj")
        
        command = Command("test")
        ctx = Context(
            command,
            parent=parent_ctx,
            info_name="test_command",
            obj="custom_obj",
            auto_envvar_prefix="TEST",
            default_map={"key": "value"},
            terminal_width=80,
            max_content_width=100,
            resilient_parsing=True,
            allow_extra_args=True,
            allow_interspersed_args=False,
            ignore_unknown_options=True,
            help_option_names=["--help", "-h"],
            token_normalize_func=lambda x: x.upper(),
            color=False,
            show_default=True
        )
        
        assert ctx.parent == parent_ctx
        assert ctx.command == command
        assert ctx.info_name == "test_command"
        assert ctx.obj == "custom_obj"  # Should not inherit from parent
        assert ctx.auto_envvar_prefix == "TEST"
        assert ctx.default_map == {"key": "value"}
        assert ctx.terminal_width == 80
        assert ctx.max_content_width == 100
        assert ctx.resilient_parsing is True
        assert ctx.allow_extra_args is True
        assert ctx.allow_interspersed_args is False
        assert ctx.ignore_unknown_options is True
        assert ctx.help_option_names == ["--help", "-h"]
        assert ctx.token_normalize_func is not None
        assert ctx.color is False
        assert ctx.show_default is True
        assert ctx._close_callbacks == []
        assert ctx._depth == 0
        assert ctx._parameter_source == {}
        assert hasattr(ctx, '_exit_stack')
