# file: src/flask/src/flask/json/tag.py:119-130
# asked: {"lines": [119, 120, 122, 123, 125, 128, 130], "branches": []}
# gained: {"lines": [119, 120, 122, 123, 125, 128, 130], "branches": []}

import pytest
import typing as t
from flask.json.tag import PassDict, TaggedJSONSerializer


class TestPassDict:
    """Test cases for PassDict JSON tag."""
    
    def test_check_returns_true_for_dict(self):
        """Test that check returns True for dict values."""
        serializer = TaggedJSONSerializer()
        tag = PassDict(serializer)
        
        assert tag.check({}) is True
        assert tag.check({"key": "value"}) is True
        assert tag.check({"nested": {"inner": "value"}}) is True
    
    def test_check_returns_false_for_non_dict(self):
        """Test that check returns False for non-dict values."""
        serializer = TaggedJSONSerializer()
        tag = PassDict(serializer)
        
        assert tag.check("string") is False
        assert tag.check(123) is False
        assert tag.check([1, 2, 3]) is False
        assert tag.check(None) is False
        assert tag.check(True) is False
    
    def test_to_json_processes_dict_values(self):
        """Test that to_json processes all values in the dict."""
        serializer = TaggedJSONSerializer()
        tag = PassDict(serializer)
        
        # Test with simple values that won't be tagged by other tags
        test_dict = {"a": "test_string", "b": 42, "c": True}
        result = tag.to_json(test_dict)
        
        # The values should be passed through unchanged since they're basic JSON types
        assert result == {"a": "test_string", "b": 42, "c": True}
    
    def test_to_json_with_nested_dicts(self):
        """Test that to_json processes nested dict values."""
        serializer = TaggedJSONSerializer()
        tag = PassDict(serializer)
        
        # Test with nested dict that should trigger PassDict again
        test_dict = {"outer": {"inner": "value"}}
        result = tag.to_json(test_dict)
        
        # The nested dict should be processed by PassDict as well
        assert result == {"outer": {"inner": "value"}}
    
    def test_to_json_with_empty_dict(self):
        """Test that to_json handles empty dict correctly."""
        serializer = TaggedJSONSerializer()
        tag = PassDict(serializer)
        
        result = tag.to_json({})
        assert result == {}
    
    def test_tag_alias(self):
        """Test that tag is an alias for to_json method."""
        serializer = TaggedJSONSerializer()
        tag = PassDict(serializer)
        
        # Verify tag and to_json produce the same results
        test_dict = {"key": "value"}
        tag_result = tag.tag(test_dict)
        to_json_result = tag.to_json(test_dict)
        
        assert tag_result == to_json_result
        
        # Test with different dict
        test_dict2 = {"a": 1, "b": 2}
        tag_result2 = tag.tag(test_dict2)
        to_json_result2 = tag.to_json(test_dict2)
        
        assert tag_result2 == to_json_result2
