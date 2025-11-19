# file: src/flask/src/flask/json/tag.py:93-116
# asked: {"lines": [93, 94, 100, 101, 103, 104, 105, 106, 107, 110, 111, 112, 114, 115, 116], "branches": []}
# gained: {"lines": [93, 94, 100, 101, 103, 104, 105, 106, 107, 110, 111, 112, 114, 115, 116], "branches": []}

import pytest
import typing as t
from flask.json.tag import TagDict, TaggedJSONSerializer


class TestTagDict:
    """Test cases for TagDict class to achieve full coverage."""
    
    def test_check_returns_true_for_valid_tagged_dict(self):
        """Test that check returns True for a dict with one key that matches a registered tag."""
        serializer = TaggedJSONSerializer()
        tag_dict = TagDict(serializer)
        
        # Create a dict with a key that matches a registered tag
        test_dict = {" di": "some_value"}
        
        result = tag_dict.check(test_dict)
        assert result is True
    
    def test_check_returns_false_for_non_dict(self):
        """Test that check returns False for non-dict values."""
        serializer = TaggedJSONSerializer()
        tag_dict = TagDict(serializer)
        
        result = tag_dict.check("not_a_dict")
        assert result is False
    
    def test_check_returns_false_for_dict_with_multiple_keys(self):
        """Test that check returns False for dicts with multiple keys."""
        serializer = TaggedJSONSerializer()
        tag_dict = TagDict(serializer)
        
        test_dict = {" di": "value1", "other_key": "value2"}
        
        result = tag_dict.check(test_dict)
        assert result is False
    
    def test_check_returns_false_for_dict_with_unregistered_tag(self):
        """Test that check returns False for dicts with keys that are not registered tags."""
        serializer = TaggedJSONSerializer()
        tag_dict = TagDict(serializer)
        
        test_dict = {"unregistered_tag": "some_value"}
        
        result = tag_dict.check(test_dict)
        assert result is False
    
    def test_to_json_transforms_dict_key(self):
        """Test that to_json transforms the dict key by adding '__' suffix."""
        serializer = TaggedJSONSerializer()
        tag_dict = TagDict(serializer)
        
        # Create a test value that will be tagged by the serializer
        test_dict = {" di": "test_value"}
        
        # The serializer.tag method will be called internally
        result = tag_dict.to_json(test_dict)
        
        # The key should have '__' suffix added
        assert list(result.keys())[0] == " di__"
    
    def test_to_python_transforms_dict_key(self):
        """Test that to_python transforms the dict key by removing '__' suffix."""
        serializer = TaggedJSONSerializer()
        tag_dict = TagDict(serializer)
        
        test_dict = {" di__": "test_value"}
        result = tag_dict.to_python(test_dict)
        
        expected = {" di": "test_value"}
        assert result == expected
