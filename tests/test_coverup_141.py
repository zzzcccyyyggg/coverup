# file: src/flask/src/flask/json/tag.py:289-295
# asked: {"lines": [289, 291, 292, 293, 295], "branches": [[291, 292], [291, 295], [292, 291], [292, 293]]}
# gained: {"lines": [289, 291, 292, 293, 295], "branches": [[291, 292], [291, 295], [292, 291], [292, 293]]}

import pytest
import typing as t
from flask.json.tag import TaggedJSONSerializer, JSONTag


class MockTag(JSONTag):
    """Mock tag for testing purposes."""
    key = "mock"
    
    def __init__(self, serializer: TaggedJSONSerializer, should_match: bool = True):
        super().__init__(serializer)
        self.should_match = should_match
        self.check_called = False
        self.tag_called = False
    
    def check(self, value: t.Any) -> bool:
        self.check_called = True
        return self.should_match
    
    def tag(self, value: t.Any) -> dict[str, t.Any]:
        self.tag_called = True
        return {"__tag__": self.key, "value": value}


def test_tag_with_matching_tag():
    """Test that tag() returns tagged representation when a tag matches."""
    serializer = TaggedJSONSerializer()
    
    # Create a mock tag instance and manually add it to serializer
    mock_tag = MockTag(serializer, should_match=True)
    serializer.tags.clear()
    serializer.order.clear()
    serializer.tags[mock_tag.key] = mock_tag
    serializer.order.append(mock_tag)
    
    test_value = "test_value"
    result = serializer.tag(test_value)
    
    assert result == {"__tag__": "mock", "value": test_value}
    assert mock_tag.check_called
    assert mock_tag.tag_called


def test_tag_with_no_matching_tags():
    """Test that tag() returns original value when no tags match."""
    serializer = TaggedJSONSerializer()
    
    # Create a mock tag instance and manually add it to serializer
    mock_tag = MockTag(serializer, should_match=False)
    serializer.tags.clear()
    serializer.order.clear()
    serializer.tags[mock_tag.key] = mock_tag
    serializer.order.append(mock_tag)
    
    test_value = "test_value"
    result = serializer.tag(test_value)
    
    assert result == test_value
    assert mock_tag.check_called
    assert not mock_tag.tag_called


def test_tag_with_multiple_tags_first_matches():
    """Test that tag() returns first matching tag's result."""
    serializer = TaggedJSONSerializer()
    
    class FirstTag(MockTag):
        key = "first"
    
    class SecondTag(MockTag):
        key = "second"
    
    first_tag = FirstTag(serializer, should_match=True)
    second_tag = SecondTag(serializer, should_match=True)
    
    # Manually add tags to serializer
    serializer.tags.clear()
    serializer.order.clear()
    serializer.tags[first_tag.key] = first_tag
    serializer.tags[second_tag.key] = second_tag
    serializer.order.append(first_tag)
    serializer.order.append(second_tag)
    
    test_value = "test_value"
    result = serializer.tag(test_value)
    
    assert result == {"__tag__": "first", "value": test_value}
    assert first_tag.check_called
    assert first_tag.tag_called
    assert not second_tag.check_called
    assert not second_tag.tag_called


def test_tag_with_multiple_tags_second_matches():
    """Test that tag() returns second matching tag when first doesn't match."""
    serializer = TaggedJSONSerializer()
    
    class FirstTag(MockTag):
        key = "first"
    
    class SecondTag(MockTag):
        key = "second"
    
    first_tag = FirstTag(serializer, should_match=False)
    second_tag = SecondTag(serializer, should_match=True)
    
    # Manually add tags to serializer
    serializer.tags.clear()
    serializer.order.clear()
    serializer.tags[first_tag.key] = first_tag
    serializer.tags[second_tag.key] = second_tag
    serializer.order.append(first_tag)
    serializer.order.append(second_tag)
    
    test_value = "test_value"
    result = serializer.tag(test_value)
    
    assert result == {"__tag__": "second", "value": test_value}
    assert first_tag.check_called
    assert not first_tag.tag_called
    assert second_tag.check_called
    assert second_tag.tag_called
