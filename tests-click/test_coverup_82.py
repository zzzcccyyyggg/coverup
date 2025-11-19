# file: src/click/src/click/core.py:3326-3345
# asked: {"lines": [3326, 3329, 3333, 3336, 3337, 3340, 3342, 3343, 3345], "branches": [[3333, 3336], [3333, 3342], [3336, 3337], [3336, 3340], [3342, 3343], [3342, 3345]]}
# gained: {"lines": [3326, 3329, 3333, 3336, 3337, 3340, 3342, 3343, 3345], "branches": [[3333, 3336], [3333, 3342], [3336, 3337], [3336, 3340], [3342, 3343], [3342, 3345]]}

import pytest
from click.core import Argument
from click._utils import UNSET


class TestArgumentInit:
    def test_required_none_no_default_nargs_positive(self):
        """Test required=None with no default and nargs > 0 -> required=True"""
        arg = Argument(["name"], required=None, nargs=2)
        assert arg.required is True

    def test_required_none_no_default_nargs_zero(self):
        """Test required=None with no default and nargs=0 -> required=False"""
        arg = Argument(["name"], required=None, nargs=0)
        assert arg.required is False

    def test_required_none_no_default_nargs_default(self):
        """Test required=None with no default and default nargs=1 -> required=True"""
        arg = Argument(["name"], required=None)
        assert arg.required is True

    def test_required_none_with_default(self):
        """Test required=None with default value -> required=False"""
        arg = Argument(["name"], required=None, default="test")
        assert arg.required is False

    def test_required_explicit_true(self):
        """Test required=True explicitly set"""
        arg = Argument(["name"], required=True)
        assert arg.required is True

    def test_required_explicit_false(self):
        """Test required=False explicitly set"""
        arg = Argument(["name"], required=False)
        assert arg.required is False

    def test_multiple_keyword_raises_error(self):
        """Test that 'multiple' keyword argument raises TypeError"""
        with pytest.raises(TypeError, match=r"__init__\(\) got an unexpected keyword argument 'multiple'\."):
            Argument(["name"], multiple=True)
