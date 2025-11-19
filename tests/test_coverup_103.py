# file: src/flask/src/flask/json/tag.py:205-216
# asked: {"lines": [205, 206, 207, 209, 210, 212, 213, 215, 216], "branches": []}
# gained: {"lines": [205, 206, 207, 209, 210, 212, 213, 215, 216], "branches": []}

import pytest
from datetime import datetime
from flask.json.tag import TagDateTime, TaggedJSONSerializer


class TestTagDateTime:
    """Test cases for TagDateTime class to achieve full coverage."""
    
    def test_check_with_datetime_returns_true(self):
        """Test that check returns True for datetime objects."""
        serializer = TaggedJSONSerializer()
        tag = TagDateTime(serializer)
        value = datetime(2023, 1, 1, 12, 0, 0)
        assert tag.check(value) is True
    
    def test_check_with_non_datetime_returns_false(self):
        """Test that check returns False for non-datetime objects."""
        serializer = TaggedJSONSerializer()
        tag = TagDateTime(serializer)
        value = "2023-01-01 12:00:00"
        assert tag.check(value) is False
    
    def test_to_json_converts_datetime_to_http_date(self):
        """Test that to_json converts datetime to HTTP date string."""
        serializer = TaggedJSONSerializer()
        tag = TagDateTime(serializer)
        value = datetime(2023, 1, 1, 12, 0, 0)
        result = tag.to_json(value)
        assert isinstance(result, str)
        assert "Sun, 01 Jan 2023 12:00:00 GMT" in result
    
    def test_to_python_parses_http_date_to_datetime(self):
        """Test that to_python parses HTTP date string to datetime."""
        serializer = TaggedJSONSerializer()
        tag = TagDateTime(serializer)
        value = "Sun, 01 Jan 2023 12:00:00 GMT"
        result = tag.to_python(value)
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.minute == 0
        assert result.second == 0
