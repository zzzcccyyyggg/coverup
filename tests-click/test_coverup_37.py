# file: src/click/src/click/types.py:618-658
# asked: {"lines": [618, 619, 634, 636, 638, 639, 640, 641, 642, 644, 645, 648, 649, 651, 652, 653, 658], "branches": [[648, 0], [648, 649], [652, 653], [652, 658]]}
# gained: {"lines": [618, 619, 634, 636, 638, 639, 640, 641, 642, 644, 645, 648, 649, 651, 652, 653, 658], "branches": [[648, 0], [648, 649], [652, 653], [652, 658]]}

import pytest
import click
from click.types import FloatRange


class TestFloatRange:
    """Test cases for FloatRange class to achieve full coverage."""
    
    def test_init_with_open_bounds_and_clamp_raises_error(self):
        """Test that FloatRange raises TypeError when open bounds and clamp are both enabled."""
        with pytest.raises(TypeError, match="Clamping is not supported for open bounds."):
            FloatRange(min=0.0, max=1.0, min_open=True, clamp=True)
        
        with pytest.raises(TypeError, match="Clamping is not supported for open bounds."):
            FloatRange(min=0.0, max=1.0, max_open=True, clamp=True)
            
        with pytest.raises(TypeError, match="Clamping is not supported for open bounds."):
            FloatRange(min=0.0, max=1.0, min_open=True, max_open=True, clamp=True)

    def test_clamp_with_closed_bound(self):
        """Test _clamp method with closed bounds."""
        float_range = FloatRange(min=0.0, max=1.0, clamp=True)
        result = float_range._clamp(0.5, 1, False)
        assert result == 0.5

    def test_clamp_with_open_bound_raises_error(self):
        """Test _clamp method with open bounds raises RuntimeError."""
        float_range = FloatRange(min=0.0, max=1.0, min_open=True)
        with pytest.raises(RuntimeError, match="Clamping is not supported for open bounds."):
            float_range._clamp(0.5, 1, True)
