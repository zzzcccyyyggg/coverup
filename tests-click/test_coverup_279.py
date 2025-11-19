# file: src/click/src/click/types.py:547-555
# asked: {"lines": [547, 555], "branches": []}
# gained: {"lines": [547, 555], "branches": []}

import pytest
import typing as t
from click.types import _NumberRangeBase

class TestNumberRangeBaseClamp:
    """Test cases for _NumberRangeBase._clamp method."""
    
    def test_clamp_not_implemented(self):
        """Test that _clamp raises NotImplementedError."""
        base = _NumberRangeBase()
        with pytest.raises(NotImplementedError):
            base._clamp(10.0, 1, False)
