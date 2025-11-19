# file: src/click/src/click/types.py:610-615
# asked: {"lines": [610, 611, 612, 614, 615], "branches": []}
# gained: {"lines": [610, 611, 612, 614, 615], "branches": []}

import pytest
import click


class TestFloatParamType:
    def test_repr(self):
        """Test that FloatParamType.__repr__ returns 'FLOAT'."""
        param_type = click.types.FloatParamType()
        assert repr(param_type) == "FLOAT"
