# file: src/click/src/click/core.py:2219-2220
# asked: {"lines": [2219, 2220], "branches": []}
# gained: {"lines": [2219, 2220], "branches": []}

import pytest
from click.core import Option, Argument


class TestParameterRepr:
    def test_option_repr_with_name(self):
        """Test that Option.__repr__ returns the expected string format when name is set."""
        option = Option(["--test-option"])
        assert repr(option) == "<Option test_option>"

    def test_argument_repr_with_name(self):
        """Test that Argument.__repr__ returns the expected string format when name is set."""
        argument = Argument(["test_arg"])
        assert repr(argument) == "<Argument test_arg>"

    def test_option_repr_with_expose_value_false(self):
        """Test that Option.__repr__ works when expose_value=False and no name can be determined."""
        option = Option([], expose_value=False)
        assert repr(option) == "<Option None>"

    def test_argument_repr_with_expose_value_false(self):
        """Test that Argument.__repr__ works when expose_value=False and no name can be determined."""
        argument = Argument([], expose_value=False)
        assert repr(argument) == "<Argument None>"
