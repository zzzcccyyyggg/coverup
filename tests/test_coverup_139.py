# file: src/flask/src/flask/app.py:69-73
# asked: {"lines": [69, 70, 71, 73], "branches": [[70, 71], [70, 73]]}
# gained: {"lines": [69, 70, 71, 73], "branches": [[70, 71], [70, 73]]}

import pytest
from datetime import timedelta
from flask.app import _make_timedelta


class TestMakeTimedelta:
    def test_none_value_returns_none(self):
        """Test that None value returns None"""
        result = _make_timedelta(None)
        assert result is None

    def test_timedelta_value_returns_same(self):
        """Test that timedelta value returns the same timedelta"""
        td = timedelta(days=1, hours=2, minutes=3)
        result = _make_timedelta(td)
        assert result == td

    def test_int_value_returns_timedelta_with_seconds(self):
        """Test that int value returns timedelta with seconds"""
        result = _make_timedelta(3600)
        assert result == timedelta(seconds=3600)
