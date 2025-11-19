# file: src/click/src/click/shell_completion.py:503-525
# asked: {"lines": [503, 511, 512, 514, 516, 517, 518, 519, 521, 522, 523], "branches": [[511, 512], [511, 514]]}
# gained: {"lines": [503, 511, 512, 514, 516, 517, 518, 519, 521, 522, 523], "branches": [[511, 512], [511, 514]]}

import pytest
from click.core import Argument, Context, Parameter, ParameterSource
from click.shell_completion import _is_incomplete_argument


class MockCommand:
    """Mock command for testing Context creation."""
    allow_extra_args = False
    allow_interspersed_args = True
    ignore_unknown_options = False


class MockParameter:
    """Mock parameter for testing non-Argument parameters."""
    def __init__(self):
        pass


class TestIsIncompleteArgument:
    """Test cases for _is_incomplete_argument function."""

    def test_non_argument_parameter_returns_false(self):
        """Test that non-Argument parameters return False."""
        ctx = Context(MockCommand())
        param = MockParameter()
        
        result = _is_incomplete_argument(ctx, param)
        assert result is False

    def test_argument_with_nargs_minus_one_returns_true(self):
        """Test that Argument with nargs=-1 returns True."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=-1)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is True

    def test_argument_with_commandline_source_returns_false(self):
        """Test that Argument with COMMANDLINE source returns False."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=1)
        ctx.params[param.name] = "value"
        ctx.set_parameter_source(param.name, ParameterSource.COMMANDLINE)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is False

    def test_argument_with_nargs_greater_than_one_and_insufficient_values(self):
        """Test that Argument with nargs>1 and insufficient values returns True."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=3)
        ctx.params[param.name] = ("value1", "value2")  # Only 2 values, need 3
        ctx.set_parameter_source(param.name, ParameterSource.DEFAULT)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is True

    def test_argument_with_nargs_greater_than_one_and_sufficient_values(self):
        """Test that Argument with nargs>1 and sufficient values returns False."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=2)
        ctx.params[param.name] = ("value1", "value2")  # Exactly 2 values
        ctx.set_parameter_source(param.name, ParameterSource.COMMANDLINE)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is False

    def test_argument_with_nargs_greater_than_one_and_list_values(self):
        """Test that Argument with nargs>1 and list values works correctly."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=3)
        ctx.params[param.name] = ["value1", "value2"]  # Only 2 values in list, need 3
        ctx.set_parameter_source(param.name, ParameterSource.DEFAULT)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is True

    def test_argument_with_nargs_one_and_non_commandline_source(self):
        """Test that Argument with nargs=1 and non-COMMANDLINE source returns True."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=1)
        ctx.params[param.name] = "value"
        ctx.set_parameter_source(param.name, ParameterSource.DEFAULT)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is True

    def test_argument_with_nargs_zero_and_commandline_source(self):
        """Test that Argument with nargs=0 and COMMANDLINE source returns False."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=0)
        ctx.params[param.name] = None
        ctx.set_parameter_source(param.name, ParameterSource.COMMANDLINE)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is False

    def test_argument_with_nargs_greater_than_one_and_non_tuple_value(self):
        """Test that Argument with nargs>1 and non-tuple/list value returns False."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=3)
        ctx.params[param.name] = "single_value"  # Not a tuple/list
        ctx.set_parameter_source(param.name, ParameterSource.COMMANDLINE)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is False

    def test_argument_with_nargs_one_and_no_value(self):
        """Test that Argument with nargs=1 and no value returns True."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=1)
        # Don't set any value in ctx.params
        ctx.set_parameter_source(param.name, ParameterSource.DEFAULT)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is True

    def test_argument_with_nargs_greater_than_one_and_no_value(self):
        """Test that Argument with nargs>1 and no value returns True."""
        ctx = Context(MockCommand())
        param = Argument(["test_arg"], nargs=3)
        # Don't set any value in ctx.params
        ctx.set_parameter_source(param.name, ParameterSource.DEFAULT)
        
        result = _is_incomplete_argument(ctx, param)
        assert result is True
