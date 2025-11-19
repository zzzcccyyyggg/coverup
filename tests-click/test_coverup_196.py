# file: src/click/src/click/parser.py:120-124
# asked: {"lines": [120, 121, 122, 123, 124], "branches": [[121, 122], [121, 123]]}
# gained: {"lines": [120, 121, 122, 123, 124], "branches": [[121, 122], [121, 123]]}

import pytest
from click.core import Context, Command
from click.parser import _normalize_opt, _split_opt


class TestNormalizeOpt:
    """Test cases for _normalize_opt function to achieve full coverage."""
    
    def test_normalize_opt_with_none_context(self):
        """Test _normalize_opt when ctx is None."""
        # When ctx is None, should return the opt unchanged
        result = _normalize_opt("--option", None)
        assert result == "--option"
    
    def test_normalize_opt_with_context_no_normalize_func(self):
        """Test _normalize_opt when ctx.token_normalize_func is None."""
        # Create a context with no token_normalize_func
        command = Command("test")
        ctx = Context(command=command)
        ctx.token_normalize_func = None
        
        # Should return the opt unchanged
        result = _normalize_opt("--option", ctx)
        assert result == "--option"
    
    def test_normalize_opt_with_single_dash_and_normalize_func(self):
        """Test _normalize_opt with single dash option and normalize function."""
        # Create a context with a token_normalize_func
        command = Command("test")
        ctx = Context(command=command)
        ctx.token_normalize_func = lambda x: x.upper()
        
        # Test with single dash option
        result = _normalize_opt("-o", ctx)
        assert result == "-O"
    
    def test_normalize_opt_with_double_dash_and_normalize_func(self):
        """Test _normalize_opt with double dash option and normalize function."""
        # Create a context with a token_normalize_func
        command = Command("test")
        ctx = Context(command=command)
        ctx.token_normalize_func = lambda x: x.upper()
        
        # Test with double dash option
        result = _normalize_opt("--option", ctx)
        assert result == "--OPTION"
    
    def test_normalize_opt_with_no_prefix_and_normalize_func(self):
        """Test _normalize_opt with no prefix option and normalize function."""
        # Create a context with a token_normalize_func
        command = Command("test")
        ctx = Context(command=command)
        ctx.token_normalize_func = lambda x: x.upper()
        
        # Test with no prefix (alphanumeric first character)
        result = _normalize_opt("option", ctx)
        assert result == "OPTION"
