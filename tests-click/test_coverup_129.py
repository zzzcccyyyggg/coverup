# file: src/click/src/click/core.py:2234-2246
# asked: {"lines": [2234, 2235, 2236, 2238, 2240, 2241, 2243, 2244, 2246], "branches": [[2235, 2236], [2235, 2238], [2240, 2241], [2240, 2243], [2243, 2244], [2243, 2246]]}
# gained: {"lines": [2234, 2235, 2236, 2238, 2240, 2241, 2243, 2244, 2246], "branches": [[2235, 2236], [2235, 2238], [2240, 2241], [2240, 2243], [2243, 2244], [2243, 2246]]}

import pytest
from click.core import Context, Option, Command
from click.types import ParamType


class MockParamType(ParamType):
    """Mock ParamType for testing get_metavar behavior."""
    name = "mocktype"
    
    def __init__(self, metavar_return=None):
        self.metavar_return = metavar_return
    
    def get_metavar(self, param, ctx):
        return self.metavar_return


class TestParameterMakeMetavar:
    """Test cases for Parameter.make_metavar method to achieve full coverage."""
    
    def test_make_metavar_with_explicit_metavar(self):
        """Test when metavar is explicitly set."""
        ctx = Context(Command("test"))
        param = Option(["--test"], metavar="EXPLICIT")
        result = param.make_metavar(ctx)
        assert result == "EXPLICIT"
    
    def test_make_metavar_with_type_get_metavar_returning_value(self):
        """Test when type.get_metavar returns a value."""
        ctx = Context(Command("test"))
        mock_type = MockParamType(metavar_return="FROM_TYPE")
        param = Option(["--test"], type=mock_type)
        result = param.make_metavar(ctx)
        assert result == "FROM_TYPE"
    
    def test_make_metavar_with_type_get_metavar_returning_none(self):
        """Test when type.get_metavar returns None."""
        ctx = Context(Command("test"))
        mock_type = MockParamType(metavar_return=None)
        param = Option(["--test"], type=mock_type)
        result = param.make_metavar(ctx)
        assert result == "MOCKTYPE"
    
    def test_make_metavar_with_nargs_not_1(self):
        """Test when nargs is not 1 (adds ellipsis)."""
        ctx = Context(Command("test"))
        mock_type = MockParamType(metavar_return=None)
        param = Option(["--test"], type=mock_type, nargs=2)
        result = param.make_metavar(ctx)
        assert result == "MOCKTYPE..."
    
    def test_make_metavar_with_nargs_1(self):
        """Test when nargs is 1 (no ellipsis)."""
        ctx = Context(Command("test"))
        mock_type = MockParamType(metavar_return=None)
        param = Option(["--test"], type=mock_type, nargs=1)
        result = param.make_metavar(ctx)
        assert result == "MOCKTYPE"
    
    def test_make_metavar_with_type_get_metavar_and_nargs_not_1(self):
        """Test when type.get_metavar returns value and nargs is not 1."""
        ctx = Context(Command("test"))
        mock_type = MockParamType(metavar_return="CUSTOM")
        param = Option(["--test"], type=mock_type, nargs=3)
        result = param.make_metavar(ctx)
        assert result == "CUSTOM..."
