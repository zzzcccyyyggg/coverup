# file: src/flask/src/flask/sansio/app.py:52-56
# asked: {"lines": [52, 53, 54, 56], "branches": [[53, 54], [53, 56]]}
# gained: {"lines": [52, 53, 54, 56], "branches": [[53, 54], [53, 56]]}

import pytest
from datetime import timedelta
from flask.sansio.app import _make_timedelta

class TestMakeTimedelta:
    
    def test_make_timedelta_none(self):
        """Test that None input returns None."""
        result = _make_timedelta(None)
        assert result is None
    
    def test_make_timedelta_timedelta(self):
        """Test that timedelta input returns the same timedelta."""
        input_td = timedelta(days=1, hours=2, minutes=30)
        result = _make_timedelta(input_td)
        assert result == input_td
        assert result is input_td
    
    def test_make_timedelta_int(self):
        """Test that integer input converts to timedelta with seconds."""
        result = _make_timedelta(3600)
        assert result == timedelta(seconds=3600)
        assert isinstance(result, timedelta)
    
    def test_make_timedelta_zero_int(self):
        """Test that zero integer input converts to zero timedelta."""
        result = _make_timedelta(0)
        assert result == timedelta(seconds=0)
        assert isinstance(result, timedelta)
