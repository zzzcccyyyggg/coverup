# file: src/flask/src/flask/json/tag.py:297-307
# asked: {"lines": [297, 299, 300, 302, 304, 305, 307], "branches": [[299, 300], [299, 302], [304, 305], [304, 307]]}
# gained: {"lines": [297, 299, 300, 302, 304, 305, 307], "branches": [[299, 300], [299, 302], [304, 305], [304, 307]]}

import pytest
import typing as t
from flask.json.tag import TaggedJSONSerializer, JSONTag


class MockTag(JSONTag):
    """Mock tag for testing purposes."""
    key = "test_tag"
    
    def check(self, value: t.Any) -> bool:
        return isinstance(value, str) and value == "test_value"
    
    def to_json(self, value: t.Any) -> t.Any:
        return {"tagged": value}
    
    def to_python(self, value: t.Any) -> t.Any:
        return f"untagged_{value['tagged']}"


def test_untag_empty_dict():
    """Test untag with empty dict (line 299-300)."""
    serializer = TaggedJSONSerializer()
    result = serializer.untag({})
    assert result == {}


def test_untag_multiple_keys():
    """Test untag with dict containing multiple keys (line 299-300)."""
    serializer = TaggedJSONSerializer()
    result = serializer.untag({"key1": "value1", "key2": "value2"})
    assert result == {"key1": "value1", "key2": "value2"}


def test_untag_unknown_tag():
    """Test untag with unknown tag key (line 304-305)."""
    serializer = TaggedJSONSerializer()
    result = serializer.untag({"unknown_tag": "some_value"})
    assert result == {"unknown_tag": "some_value"}


def test_untag_valid_tag():
    """Test untag with valid tag key (line 307)."""
    serializer = TaggedJSONSerializer()
    mock_tag = MockTag(serializer)
    
    # Register the mock tag
    serializer.tags["test_tag"] = mock_tag
    
    result = serializer.untag({"test_tag": {"tagged": "test_value"}})
    assert result == "untagged_test_value"
