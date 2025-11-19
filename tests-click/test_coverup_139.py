# file: src/click/src/click/types.py:584-607
# asked: {"lines": [584, 585, 599, 601, 604, 605, 607], "branches": [[604, 605], [604, 607]]}
# gained: {"lines": [584, 585, 599, 601, 604, 605, 607], "branches": [[604, 605], [604, 607]]}

import pytest
import click
from click.types import IntRange


class TestIntRangeClamp:
    """Test cases for IntRange._clamp method to achieve full coverage."""
    
    def test_clamp_with_closed_boundary(self):
        """Test _clamp method when open=False (closed boundary)."""
        int_range = IntRange(min=0, max=100)
        result = int_range._clamp(50, 1, False)
        assert result == 50
    
    def test_clamp_with_open_boundary_positive_direction(self):
        """Test _clamp method when open=True with positive direction."""
        int_range = IntRange(min=0, max=100)
        result = int_range._clamp(50, 1, True)
        assert result == 51
    
    def test_clamp_with_open_boundary_negative_direction(self):
        """Test _clamp method when open=True with negative direction."""
        int_range = IntRange(min=0, max=100)
        result = int_range._clamp(50, -1, True)
        assert result == 49
