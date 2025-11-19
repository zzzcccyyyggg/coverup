# file: src/click/src/click/core.py:3384-3385
# asked: {"lines": [3384, 3385], "branches": []}
# gained: {"lines": [3384, 3385], "branches": []}

import pytest
import click
from click.core import Argument, Context


class TestArgumentGetUsagePieces:
    """Test cases for Argument.get_usage_pieces method to achieve full coverage."""
    
    def test_get_usage_pieces_calls_make_metavar(self):
        """Test that get_usage_pieces returns a list containing the result of make_metavar."""
        # Create a simple Argument instance
        arg = Argument(['test_arg'])
        
        # Create a mock context
        ctx = Context(click.Command('test_command'))
        
        # Call get_usage_pieces and verify it returns a list with make_metavar result
        result = arg.get_usage_pieces(ctx)
        
        # Verify the result is a list containing the metavar
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == arg.make_metavar(ctx)
        
    def test_get_usage_pieces_with_different_argument_types(self):
        """Test get_usage_pieces with various argument configurations."""
        # Test with required argument
        required_arg = Argument(['required_arg'], required=True)
        ctx = Context(click.Command('test_command'))
        result = required_arg.get_usage_pieces(ctx)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == required_arg.make_metavar(ctx)
        
        # Test with optional argument
        optional_arg = Argument(['optional_arg'], required=False)
        result = optional_arg.get_usage_pieces(ctx)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == optional_arg.make_metavar(ctx)
        
        # Test with custom metavar
        custom_arg = Argument(['custom_arg'], metavar='CUSTOM')
        result = custom_arg.get_usage_pieces(ctx)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == custom_arg.make_metavar(ctx)
