# file: src/click/src/click/types.py:576-581
# asked: {"lines": [576, 577, 578, 580, 581], "branches": []}
# gained: {"lines": [576, 577, 578, 580, 581], "branches": []}

import pytest
import click
from click.types import IntParamType


class TestIntParamType:
    def test_repr(self):
        """Test that IntParamType.__repr__ returns 'INT'."""
        int_type = IntParamType()
        assert repr(int_type) == "INT"
