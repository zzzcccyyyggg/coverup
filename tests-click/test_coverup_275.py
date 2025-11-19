# file: src/click/src/click/types.py:468-469
# asked: {"lines": [468, 469], "branches": []}
# gained: {"lines": [468, 469], "branches": []}

import pytest
from click.types import DateTime

def test_datetime_repr():
    """Test that DateTime.__repr__ returns 'DateTime'."""
    dt_type = DateTime()
    assert repr(dt_type) == "DateTime"
