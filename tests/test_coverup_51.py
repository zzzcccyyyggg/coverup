# file: src/flask/src/flask/json/tag.py:60-90
# asked: {"lines": [60, 61, 63, 67, 69, 71, 73, 75, 77, 80, 82, 85, 87, 90], "branches": []}
# gained: {"lines": [60, 61, 63, 67, 69, 71, 73, 75, 77, 80, 82, 85, 87, 90], "branches": []}

import pytest
import typing as t
from flask.json.tag import JSONTag, TaggedJSONSerializer


class TestJSONTag:
    """Test cases for the JSONTag base class."""
    
    def test_json_tag_initialization(self):
        """Test that JSONTag can be initialized with a serializer."""
        serializer = TaggedJSONSerializer()
        tag = JSONTag(serializer)
        assert tag.serializer is serializer
    
    def test_json_tag_check_not_implemented(self):
        """Test that check method raises NotImplementedError."""
        serializer = TaggedJSONSerializer()
        tag = JSONTag(serializer)
        with pytest.raises(NotImplementedError):
            tag.check("test_value")
    
    def test_json_tag_to_json_not_implemented(self):
        """Test that to_json method raises NotImplementedError."""
        serializer = TaggedJSONSerializer()
        tag = JSONTag(serializer)
        with pytest.raises(NotImplementedError):
            tag.to_json("test_value")
    
    def test_json_tag_to_python_not_implemented(self):
        """Test that to_python method raises NotImplementedError."""
        serializer = TaggedJSONSerializer()
        tag = JSONTag(serializer)
        with pytest.raises(NotImplementedError):
            tag.to_python("test_value")
    
    def test_json_tag_tag_method_with_empty_key(self):
        """Test the tag method when key is empty string."""
        serializer = TaggedJSONSerializer()
        
        class TestTag(JSONTag):
            key = ""
            
            def check(self, value: t.Any) -> bool:
                return isinstance(value, str)
            
            def to_json(self, value: t.Any) -> t.Any:
                return f"processed_{value}"
            
            def to_python(self, value: t.Any) -> t.Any:
                return value.replace("processed_", "")
        
        tag = TestTag(serializer)
        result = tag.tag("test_value")
        assert result == {"": "processed_test_value"}
    
    def test_json_tag_tag_method_with_custom_key(self):
        """Test the tag method when key is a custom string."""
        serializer = TaggedJSONSerializer()
        
        class TestTag(JSONTag):
            key = "custom_tag"
            
            def check(self, value: t.Any) -> bool:
                return isinstance(value, int)
            
            def to_json(self, value: t.Any) -> t.Any:
                return value * 2
            
            def to_python(self, value: t.Any) -> t.Any:
                return value // 2
        
        tag = TestTag(serializer)
        result = tag.tag(5)
        assert result == {"custom_tag": 10}
