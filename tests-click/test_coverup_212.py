# file: src/click/src/click/types.py:439-443
# asked: {"lines": [439, 440, 441, 442, 443], "branches": []}
# gained: {"lines": [439, 440, 441, 442, 443], "branches": []}

import pytest
from click.types import DateTime
from datetime import datetime

class TestDateTime:
    def test_try_to_convert_date_success(self):
        """Test _try_to_convert_date with valid date string and format."""
        dt = DateTime()
        result = dt._try_to_convert_date("2023-01-15", "%Y-%m-%d")
        assert result == datetime(2023, 1, 15)
    
    def test_try_to_convert_date_failure(self):
        """Test _try_to_convert_date with invalid date string that raises ValueError."""
        dt = DateTime()
        result = dt._try_to_convert_date("invalid-date", "%Y-%m-%d")
        assert result is None
    
    def test_try_to_convert_date_invalid_format(self):
        """Test _try_to_convert_date with valid date but wrong format."""
        dt = DateTime()
        result = dt._try_to_convert_date("2023-01-15", "%d/%m/%Y")
        assert result is None
