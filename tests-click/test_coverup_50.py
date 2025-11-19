# file: src/click/src/click/core.py:2985-3028
# asked: {"lines": [2985, 2986, 2987, 2989, 2991, 2994, 2996, 2997, 2999, 3000, 3002, 3004, 3006, 3007, 3009, 3011, 3012, 3013, 3014, 3015, 3017, 3018, 3019, 3020, 3021, 3022, 3024, 3025, 3026, 3028], "branches": [[2986, 2987], [2986, 2989], [2996, 2997], [2996, 2999], [2999, 3000], [2999, 3002], [3006, 3007], [3006, 3009], [3013, 3014], [3013, 3017], [3017, 3018], [3017, 3019], [3019, 3020], [3019, 3021], [3021, 3022], [3021, 3024], [3024, 3025], [3024, 3028]]}
# gained: {"lines": [2985, 2986, 2987, 2989, 2991, 2994, 2996, 2997, 2999, 3000, 3002, 3004, 3006, 3007, 3009, 3011, 3012, 3013, 3014, 3015, 3017, 3018, 3019, 3020, 3021, 3022, 3024, 3025, 3026, 3028], "branches": [[2986, 2987], [2986, 2989], [2996, 2997], [2996, 2999], [2999, 3000], [2999, 3002], [3006, 3007], [3006, 3009], [3013, 3014], [3013, 3017], [3017, 3018], [3017, 3019], [3019, 3020], [3019, 3021], [3021, 3022], [3021, 3024], [3024, 3025], [3024, 3028]]}

import pytest
from click.core import Option, Context, Command
from click.formatting import join_options
import collections.abc as cabc
from gettext import gettext as _

class TestOptionGetHelpRecord:
    def test_get_help_record_hidden(self):
        """Test that hidden option returns None"""
        option = Option(['--hidden-opt'])
        option.hidden = True
        ctx = Context(Command('test'))
        result = option.get_help_record(ctx)
        assert result is None

    def test_get_help_record_with_slash_opts(self):
        """Test option with slash prefix triggers any_prefix_is_slash"""
        option = Option(['/opt'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.help = "Test help"
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "/opt" in opts_str
        assert "Test help" in help_str

    def test_get_help_record_flag_with_metavar(self):
        """Test non-flag option includes metavar"""
        option = Option(['--file'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.help = "File option"
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "--file" in opts_str
        assert "TEXT" in opts_str  # Default metavar for string type

    def test_get_help_record_with_secondary_opts(self):
        """Test option with secondary options"""
        option = Option(['-o', '--output'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.secondary_opts = ['--out']
        option.help = "Output option"
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "-o" in opts_str
        assert "--output" in opts_str
        assert "--out" in opts_str

    def test_get_help_record_with_extra_envvars(self):
        """Test option with envvars in extra help"""
        option = Option(['--config'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.help = "Config option"
        
        def mock_get_help_extra(ctx):
            return {"envvars": ["CONFIG_PATH", "APP_CONFIG"]}
        
        option.get_help_extra = mock_get_help_extra
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "env var: CONFIG_PATH, APP_CONFIG" in help_str

    def test_get_help_record_with_extra_default(self):
        """Test option with default in extra help"""
        option = Option(['--port'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.help = "Port option"
        
        def mock_get_help_extra(ctx):
            return {"default": "8080"}
        
        option.get_help_extra = mock_get_help_extra
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "default: 8080" in help_str

    def test_get_help_record_with_extra_range(self):
        """Test option with range in extra help"""
        option = Option(['--size'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.help = "Size option"
        
        def mock_get_help_extra(ctx):
            return {"range": "1-100"}
        
        option.get_help_extra = mock_get_help_extra
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "1-100" in help_str

    def test_get_help_record_with_extra_required(self):
        """Test option with required in extra help"""
        option = Option(['--name'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.help = "Name option"
        
        def mock_get_help_extra(ctx):
            return {"required": "required"}
        
        option.get_help_extra = mock_get_help_extra
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "required" in help_str

    def test_get_help_record_with_multiple_extra_items(self):
        """Test option with multiple extra help items"""
        option = Option(['--database'])
        option.hidden = False
        option.is_flag = False
        option.count = False
        option.help = "Database option"
        
        def mock_get_help_extra(ctx):
            return {
                "envvars": ["DB_HOST"],
                "default": "localhost",
                "required": "required"
            }
        
        option.get_help_extra = mock_get_help_extra
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "env var: DB_HOST" in help_str
        assert "default: localhost" in help_str
        assert "required" in help_str

    def test_get_help_record_no_help_with_extra(self):
        """Test option with no help text but with extra items"""
        option = Option(['--verbose'])
        option.hidden = False
        option.is_flag = True
        option.count = False
        option.help = ""
        
        def mock_get_help_extra(ctx):
            return {"default": "False"}
        
        option.get_help_extra = mock_get_help_extra
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert help_str.startswith("[")
        assert "default: False" in help_str

    def test_get_help_record_flag_option(self):
        """Test flag option doesn't include metavar"""
        option = Option(['--verbose'])
        option.hidden = False
        option.is_flag = True
        option.count = False
        option.help = "Verbose flag"
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "--verbose" in opts_str
        assert "TEXT" not in opts_str  # No metavar for flags

    def test_get_help_record_count_option(self):
        """Test count option doesn't include metavar"""
        option = Option(['-v'])
        option.hidden = False
        option.is_flag = False
        option.count = True
        option.help = "Verbose count"
        ctx = Context(Command('test'))
        
        result = option.get_help_record(ctx)
        assert result is not None
        opts_str, help_str = result
        assert "-v" in opts_str
        assert "TEXT" not in opts_str  # No metavar for count options
