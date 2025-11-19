# file: src/click/src/click/types.py:726-727
# asked: {"lines": [726, 727], "branches": []}
# gained: {"lines": [726, 727], "branches": []}

import pytest
from click.types import BoolParamType


class TestBoolParamType:
    def test_repr(self):
        """Test that BoolParamType.__repr__ returns 'BOOL'."""
        bool_type = BoolParamType()
        result = repr(bool_type)
        assert result == "BOOL"
