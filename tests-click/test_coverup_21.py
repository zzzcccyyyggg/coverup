# file: src/click/src/click/core.py:2294-2335
# asked: {"lines": [2294, 2308, 2311, 2312, 2313, 2314, 2317, 2318, 2319, 2320, 2321, 2323, 2324, 2325, 2326, 2327, 2329, 2330, 2331, 2332, 2333, 2335], "branches": [[2317, 2318], [2317, 2323], [2319, 2320], [2319, 2323], [2323, 2324], [2323, 2329], [2325, 2326], [2325, 2329], [2329, 2330], [2329, 2335], [2331, 2332], [2331, 2335]]}
# gained: {"lines": [2294, 2308, 2311, 2312, 2313, 2314, 2317, 2318, 2319, 2320, 2321, 2323, 2324, 2325, 2326, 2327, 2329, 2330, 2331, 2332, 2333, 2335], "branches": [[2317, 2318], [2317, 2323], [2319, 2320], [2319, 2323], [2323, 2324], [2323, 2329], [2325, 2326], [2325, 2329], [2329, 2330], [2329, 2335], [2331, 2332], [2331, 2335]]}

import pytest
from click.core import Option, Context, ParameterSource
from click._utils import UNSET
from unittest.mock import Mock, MagicMock

class TestParameterConsumeValue:
    """Test cases for Parameter.consume_value method to achieve full coverage."""
    
    def test_consume_value_from_commandline(self):
        """Test when value is provided from command line."""
        param = Option(['--test-param'])
        param.name = "test_param"
        
        ctx = Mock(spec=Context)
        opts = {"test_param": "commandline_value"}
        
        value, source = param.consume_value(ctx, opts)
        
        assert value == "commandline_value"
        assert source == ParameterSource.COMMANDLINE
    
    def test_consume_value_from_envvar(self):
        """Test when value is sourced from environment variable."""
        param = Option(['--test-param'])
        param.name = "test_param"
        
        ctx = Mock(spec=Context)
        opts = {}
        
        # Mock value_from_envvar to return a value
        param.value_from_envvar = Mock(return_value="envvar_value")
        
        value, source = param.consume_value(ctx, opts)
        
        assert value == "envvar_value"
        assert source == ParameterSource.ENVIRONMENT
        param.value_from_envvar.assert_called_once_with(ctx)
    
    def test_consume_value_from_default_map(self):
        """Test when value is sourced from default map."""
        param = Option(['--test-param'])
        param.name = "test_param"
        
        ctx = Mock(spec=Context)
        ctx.lookup_default = Mock(return_value="default_map_value")
        opts = {}
        
        # Mock value_from_envvar to return None (no env var)
        param.value_from_envvar = Mock(return_value=None)
        
        value, source = param.consume_value(ctx, opts)
        
        assert value == "default_map_value"
        assert source == ParameterSource.DEFAULT_MAP
        ctx.lookup_default.assert_called_once_with("test_param")
    
    def test_consume_value_from_default(self):
        """Test when value is sourced from parameter default."""
        param = Option(['--test-param'])
        param.name = "test_param"
        
        ctx = Mock(spec=Context)
        ctx.lookup_default = Mock(return_value=UNSET)
        opts = {}
        
        # Mock value_from_envvar to return None (no env var)
        param.value_from_envvar = Mock(return_value=None)
        # Mock get_default to return a default value
        param.get_default = Mock(return_value="default_value")
        
        value, source = param.consume_value(ctx, opts)
        
        assert value == "default_value"
        assert source == ParameterSource.DEFAULT
        param.get_default.assert_called_once_with(ctx)
    
    def test_consume_value_remains_unset(self):
        """Test when no value is found from any source."""
        param = Option(['--test-param'])
        param.name = "test_param"
        
        ctx = Mock(spec=Context)
        ctx.lookup_default = Mock(return_value=UNSET)
        opts = {}
        
        # Mock value_from_envvar to return None (no env var)
        param.value_from_envvar = Mock(return_value=None)
        # Mock get_default to return UNSET (no default)
        param.get_default = Mock(return_value=UNSET)
        
        value, source = param.consume_value(ctx, opts)
        
        assert value is UNSET
        assert source == ParameterSource.DEFAULT
    
    def test_consume_value_envvar_returns_unset(self):
        """Test when envvar returns UNSET (edge case)."""
        param = Option(['--test-param'])
        param.name = "test_param"
        
        ctx = Mock(spec=Context)
        ctx.lookup_default = Mock(return_value="default_map_value")
        opts = {}
        
        # Mock value_from_envvar to return UNSET
        param.value_from_envvar = Mock(return_value=UNSET)
        
        value, source = param.consume_value(ctx, opts)
        
        assert value == "default_map_value"
        assert source == ParameterSource.DEFAULT_MAP
    
    def test_consume_value_default_map_returns_none(self):
        """Test when default map returns None (not UNSET)."""
        param = Option(['--test-param'])
        param.name = "test_param"
        
        ctx = Mock(spec=Context)
        ctx.lookup_default = Mock(return_value=None)
        opts = {}
        
        # Mock value_from_envvar to return None (no env var)
        param.value_from_envvar = Mock(return_value=None)
        # Mock get_default to return a default value
        param.get_default = Mock(return_value="default_value")
        
        value, source = param.consume_value(ctx, opts)
        
        # When default_map returns None (not UNSET), it should be used as the value
        assert value is None
        assert source == ParameterSource.DEFAULT_MAP
