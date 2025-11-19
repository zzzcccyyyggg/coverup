# file: src/click/src/click/core.py:3353-3365
# asked: {"lines": [3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365], "branches": [[3354, 3355], [3354, 3356], [3357, 3358], [3357, 3359], [3359, 3360], [3359, 3361], [3361, 3362], [3361, 3363], [3363, 3364], [3363, 3365]]}
# gained: {"lines": [3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365], "branches": [[3354, 3355], [3354, 3356], [3357, 3358], [3357, 3359], [3359, 3360], [3359, 3361], [3361, 3362], [3361, 3363], [3363, 3364], [3363, 3365]]}

import pytest
import click
from click.core import Context, Argument
from click.types import ParamType

class MockParamType(ParamType):
    """A mock ParamType for testing get_metavar behavior."""
    name = "mock_type"
    
    def __init__(self, metavar_value=None):
        self.metavar_value = metavar_value
    
    def get_metavar(self, param, ctx):
        return self.metavar_value

class TestArgumentMakeMetavar:
    """Test cases for Argument.make_metavar method to achieve full coverage."""
    
    def test_make_metavar_with_explicit_metavar(self):
        """Test when metavar is explicitly set."""
        ctx = Context(click.Command('test'))
        arg = Argument(['name'], metavar='EXPLICIT')
        result = arg.make_metavar(ctx)
        assert result == 'EXPLICIT'
    
    def test_make_metavar_with_type_metavar(self):
        """Test when type provides metavar."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value='TYPE_METAVAR')
        arg = Argument(['name'], type=custom_type)
        result = arg.make_metavar(ctx)
        assert result == 'TYPE_METAVAR'
    
    def test_make_metavar_with_no_type_metavar(self):
        """Test when type returns None for metavar."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type)
        result = arg.make_metavar(ctx)
        assert result == 'NAME'
    
    def test_make_metavar_with_empty_type_metavar(self):
        """Test when type returns empty string for metavar."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value='')
        arg = Argument(['name'], type=custom_type)
        result = arg.make_metavar(ctx)
        assert result == 'NAME'
    
    def test_make_metavar_with_deprecated_and_optional(self):
        """Test when argument is deprecated and optional."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type, deprecated=True, required=False)
        result = arg.make_metavar(ctx)
        assert result == '[NAME!]'
    
    def test_make_metavar_with_optional(self):
        """Test when argument is optional (not required)."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type, required=False)
        result = arg.make_metavar(ctx)
        assert result == '[NAME]'
    
    def test_make_metavar_with_nargs_not_one(self):
        """Test when nargs is not 1."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type, nargs=2)
        result = arg.make_metavar(ctx)
        assert result == 'NAME...'
    
    def test_make_metavar_with_all_conditions(self):
        """Test when all special conditions are met: deprecated, optional, and nargs != 1."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type, deprecated=True, required=False, nargs=3)
        result = arg.make_metavar(ctx)
        assert result == '[NAME!]...'
    
    def test_make_metavar_with_optional_and_deprecated(self):
        """Test when argument is both optional and deprecated."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type, deprecated=True, required=False)
        result = arg.make_metavar(ctx)
        assert result == '[NAME!]'
    
    def test_make_metavar_with_deprecated_and_nargs(self):
        """Test when argument is deprecated and has nargs != 1."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type, deprecated=True, required=False, nargs=-1)
        result = arg.make_metavar(ctx)
        assert result == '[NAME!]...'
    
    def test_make_metavar_with_optional_and_nargs(self):
        """Test when argument is optional and has nargs != 1."""
        ctx = Context(click.Command('test'))
        custom_type = MockParamType(metavar_value=None)
        arg = Argument(['name'], type=custom_type, required=False, nargs=0)
        result = arg.make_metavar(ctx)
        assert result == '[NAME]...'
