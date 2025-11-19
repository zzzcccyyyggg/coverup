# file: src/click/src/click/core.py:2120-2189
# asked: {"lines": [2120, 2122, 2123, 2124, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2146, 2147, 2149, 2150, 2151, 2152, 2153, 2155, 2159, 2160, 2161, 2163, 2165, 2166, 2167, 2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2177, 2178, 2179, 2180, 2181, 2184, 2185, 2186, 2188], "branches": [[2159, 2160], [2159, 2165], [2160, 2161], [2160, 2163], [2177, 2178], [2178, 2179], [2178, 2184], [2184, 0], [2184, 2185]]}
# gained: {"lines": [2120, 2122, 2123, 2124, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2146, 2147, 2149, 2150, 2151, 2152, 2153, 2155, 2159, 2160, 2161, 2163, 2165, 2166, 2167, 2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2177, 2178, 2179, 2180, 2181, 2184, 2185, 2186, 2188], "branches": [[2159, 2160], [2159, 2165], [2160, 2161], [2160, 2163], [2177, 2178], [2178, 2179], [2178, 2184], [2184, 0], [2184, 2185]]}

import pytest
from click.core import Option
from click import types
from click._utils import UNSET


class TestParameterInit:
    """Test cases for Parameter.__init__ method to achieve full coverage."""
    
    def test_init_with_composite_type_and_none_nargs(self):
        """Test that composite type sets nargs to its arity when nargs is None."""
        # Create a composite type (like Tuple) that has arity > 1
        composite_type = types.Tuple([types.INT, types.STRING])
        
        param = Option(
            param_decls=["--test"],
            type=composite_type,
            nargs=None
        )
        
        # Verify that nargs was set to the composite type's arity
        assert param.nargs == composite_type.arity
        assert param.type.is_composite is True
    
    def test_init_with_non_composite_type_and_none_nargs(self):
        """Test that non-composite type sets nargs to 1 when nargs is None."""
        param = Option(
            param_decls=["--test"],
            type=types.INT,
            nargs=None
        )
        
        # Verify that nargs was set to 1 for non-composite type
        assert param.nargs == 1
        assert param.type.is_composite is False
    
    def test_init_with_composite_type_and_mismatched_nargs_debug_mode(self):
        """Test ValueError when composite type has mismatched nargs in debug mode."""
        composite_type = types.Tuple([types.INT, types.STRING])
        
        # This should raise ValueError in debug mode
        with pytest.raises(ValueError, match="'nargs' must be 2"):
            Option(
                param_decls=["--test"],
                type=composite_type,
                nargs=3  # Wrong nargs for tuple with 2 elements
            )
    
    def test_init_with_required_and_deprecated_debug_mode(self):
        """Test ValueError when parameter is both required and deprecated in debug mode."""
        # This should raise ValueError in debug mode
        with pytest.raises(ValueError, match="is deprecated and still required"):
            Option(
                param_decls=["--test"],
                required=True,
                deprecated=True
            )
    
    def test_init_with_required_and_deprecated_string_debug_mode(self):
        """Test ValueError when parameter is both required and deprecated with string message."""
        # This should raise ValueError in debug mode
        with pytest.raises(ValueError, match="is deprecated and still required"):
            Option(
                param_decls=["--test"],
                required=True,
                deprecated="This option is deprecated"
            )
    
    def test_init_with_composite_type_and_correct_nargs(self):
        """Test that composite type with correct nargs doesn't raise error."""
        composite_type = types.Tuple([types.INT, types.STRING])
        
        # This should work fine
        param = Option(
            param_decls=["--test"],
            type=composite_type,
            nargs=2  # Correct nargs for tuple with 2 elements
        )
        
        assert param.nargs == 2
        assert param.type.is_composite is True
    
    def test_init_with_deprecated_but_not_required(self):
        """Test that deprecated parameter that is not required works fine."""
        param = Option(
            param_decls=["--test"],
            required=False,
            deprecated=True
        )
        
        assert param.deprecated is True
        assert param.required is False
    
    def test_init_with_required_but_not_deprecated(self):
        """Test that required parameter that is not deprecated works fine."""
        param = Option(
            param_decls=["--test"],
            required=True,
            deprecated=False
        )
        
        assert param.deprecated is False
        assert param.required is True
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameter values set."""
        def test_callback(ctx, param, value):
            return value
        
        def test_shell_complete(ctx, param, incomplete):
            return []
        
        param = Option(
            param_decls=["--test", "-t"],
            type=types.INT,
            required=True,
            default=42,
            callback=test_callback,
            nargs=1,
            multiple=False,
            metavar="NUMBER",
            expose_value=True,
            is_eager=True,
            envvar="TEST_VAR",
            shell_complete=test_shell_complete,
            deprecated=False
        )
        
        assert param.opts == ["--test", "-t"]
        assert param.type.name == "integer"
        assert param.required is True
        assert param.default == 42
        assert param.callback is test_callback
        assert param.nargs == 1
        assert param.multiple is False
        assert param.metavar == "NUMBER"
        assert param.expose_value is True
        assert param.is_eager is True
        assert param.envvar == "TEST_VAR"
        assert param._custom_shell_complete is test_shell_complete
        assert param.deprecated is False
