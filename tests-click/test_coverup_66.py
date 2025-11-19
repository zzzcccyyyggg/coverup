# file: src/click/src/click/core.py:3030-3112
# asked: {"lines": [3030, 3031, 3033, 3034, 3036, 3037, 3038, 3039, 3040, 3042, 3044, 3045, 3046, 3048, 3053, 3054, 3056, 3057, 3059, 3061, 3062, 3064, 3065, 3066, 3068, 3069, 3070, 3072, 3073, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3094, 3096, 3097, 3099, 3100, 3102, 3104, 3106, 3107, 3109, 3110, 3112], "branches": [[3033, 3034], [3033, 3053], [3036, 3037], [3036, 3044], [3037, 3042], [3037, 3044], [3044, 3045], [3044, 3053], [3045, 3046], [3045, 3048], [3064, 3065], [3064, 3069], [3065, 3066], [3065, 3068], [3069, 3070], [3069, 3072], [3072, 3075], [3072, 3099], [3075, 3076], [3075, 3077], [3077, 3078], [3077, 3079], [3079, 3080], [3079, 3081], [3081, 3082], [3081, 3083], [3083, 3086], [3083, 3089], [3089, 3090], [3089, 3091], [3091, 3092], [3091, 3094], [3096, 3097], [3096, 3099], [3099, 3104], [3099, 3109], [3106, 3107], [3106, 3109], [3109, 3110], [3109, 3112]]}
# gained: {"lines": [3030, 3031, 3033, 3034, 3036, 3037, 3038, 3039, 3040, 3042, 3044, 3045, 3046, 3048, 3053, 3054, 3056, 3057, 3059, 3061, 3062, 3064, 3065, 3066, 3068, 3069, 3070, 3072, 3073, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3094, 3096, 3097, 3099, 3100, 3102, 3104, 3106, 3107, 3109, 3110, 3112], "branches": [[3033, 3034], [3033, 3053], [3036, 3037], [3036, 3044], [3037, 3042], [3044, 3045], [3045, 3046], [3045, 3048], [3064, 3065], [3064, 3069], [3065, 3066], [3065, 3068], [3069, 3070], [3069, 3072], [3072, 3075], [3072, 3099], [3075, 3076], [3075, 3077], [3077, 3078], [3077, 3079], [3079, 3080], [3079, 3081], [3081, 3082], [3081, 3083], [3083, 3086], [3083, 3089], [3089, 3090], [3089, 3091], [3091, 3092], [3091, 3094], [3096, 3097], [3096, 3099], [3099, 3104], [3099, 3109], [3106, 3107], [3109, 3110], [3109, 3112]]}

import pytest
import enum
from click import Option, Context, Command
from click.types import IntRange
from click._utils import UNSET

class TestOptionGetHelpExtra:
    
    def test_get_help_extra_with_envvar_autoenv(self):
        """Test envvar generation with auto_envvar_prefix and allow_from_autoenv=True"""
        command = Command("test")
        ctx = Context(command, auto_envvar_prefix="TEST")
        option = Option(["--test"], allow_from_autoenv=True, show_envvar=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "envvars" in extra
        assert extra["envvars"] == ("TEST_TEST",)
    
    def test_get_help_extra_with_envvar_list(self):
        """Test envvar with list of environment variables"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--test"], envvar=["VAR1", "VAR2"], show_envvar=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "envvars" in extra
        assert extra["envvars"] == ("VAR1", "VAR2")
    
    def test_get_help_extra_with_show_default_string(self):
        """Test show_default as string"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--test"], default="value", show_default="custom default")
        
        extra = option.get_help_extra(ctx)
        
        assert "default" in extra
        assert extra["default"] == "(custom default)"
    
    def test_get_help_extra_with_default_list(self):
        """Test default value as list"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--test"], default=["a", "b", "c"], show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "default" in extra
        assert extra["default"] == "a, b, c"
    
    def test_get_help_extra_with_default_enum(self):
        """Test default value as enum"""
        class TestEnum(enum.Enum):
            VALUE1 = "value1"
            VALUE2 = "value2"
        
        command = Command("test")
        ctx = Context(command)
        option = Option(["--test"], default=TestEnum.VALUE1, show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "default" in extra
        assert extra["default"] == "VALUE1"
    
    def test_get_help_extra_with_default_function(self):
        """Test default value as function"""
        def dynamic_default():
            return "dynamic"
        
        command = Command("test")
        ctx = Context(command)
        option = Option(["--test"], default=dynamic_default, show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "default" in extra
        assert extra["default"] == "(dynamic)"
    
    def test_get_help_extra_with_bool_flag_secondary_opts(self):
        """Test boolean flag with secondary options"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--enable/--disable"], is_flag=True, default=True, show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "default" in extra
        # Should show the primary option name without prefix when default is True
        assert extra["default"] == "enable"
    
    def test_get_help_extra_with_bool_flag_no_secondary_no_default(self):
        """Test boolean flag without secondary options and default=False"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--flag"], is_flag=True, default=False, show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        # Should not show default for boolean flag with False default
        assert "default" not in extra
    
    def test_get_help_extra_with_empty_string_default(self):
        """Test default value as empty string"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--test"], default="", show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "default" in extra
        assert extra["default"] == '""'
    
    def test_get_help_extra_with_number_range(self):
        """Test option with number range type"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--count"], type=IntRange(1, 10), show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "range" in extra
        assert extra["range"] == "1<=x<=10"
    
    def test_get_help_extra_with_count_and_range(self):
        """Test count option with range type (should not show range)"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--verbose"], count=True, type=IntRange(0, None), show_default=True)
        
        extra = option.get_help_extra(ctx)
        
        # Count options with default range (min=0, max=None) should not show range
        assert "range" not in extra
    
    def test_get_help_extra_required(self):
        """Test required option"""
        command = Command("test")
        ctx = Context(command)
        option = Option(["--required-arg"], required=True)
        
        extra = option.get_help_extra(ctx)
        
        assert "required" in extra
        assert extra["required"] == "required"
    
    def test_get_help_extra_with_ctx_show_default(self):
        """Test using context show_default when option show_default is None"""
        command = Command("test")
        ctx = Context(command, show_default=True)
        option = Option(["--test"], default="value", show_default=None)
        
        extra = option.get_help_extra(ctx)
        
        assert "default" in extra
        assert extra["default"] == "value"
    
    def test_get_help_extra_with_resilient_parsing_restored(self):
        """Test that resilient_parsing is restored after getting default"""
        command = Command("test")
        ctx = Context(command, resilient_parsing=False)
        option = Option(["--test"], default="value", show_default=True)
        
        original_resilient = ctx.resilient_parsing
        extra = option.get_help_extra(ctx)
        
        # Should restore original resilient_parsing value
        assert ctx.resilient_parsing == original_resilient
        assert "default" in extra
