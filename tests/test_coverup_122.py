# file: src/flask/src/flask/json/tag.py:133-144
# asked: {"lines": [133, 134, 135, 137, 138, 140, 141, 143, 144], "branches": []}
# gained: {"lines": [133, 134, 135, 137, 138, 140, 141, 143, 144], "branches": []}

import pytest
import typing as t
from flask.json.tag import TagTuple, TaggedJSONSerializer


class TestTagTuple:
    """Test cases for TagTuple class to achieve full coverage."""
    
    def test_check_with_tuple_returns_true(self):
        """Test that check method returns True for tuple values."""
        serializer = TaggedJSONSerializer()
        tag_tuple = TagTuple(serializer)
        
        result = tag_tuple.check((1, 2, 3))
        assert result is True
        
    def test_check_with_non_tuple_returns_false(self):
        """Test that check method returns False for non-tuple values."""
        serializer = TaggedJSONSerializer()
        tag_tuple = TagTuple(serializer)
        
        result = tag_tuple.check([1, 2, 3])
        assert result is False
        
        result = tag_tuple.check("string")
        assert result is False
        
        result = tag_tuple.check(123)
        assert result is False
        
    def test_to_json_converts_tuple_to_list_of_tagged_items(self):
        """Test that to_json converts tuple to list with tagged items."""
        serializer = TaggedJSONSerializer()
        tag_tuple = TagTuple(serializer)
        
        # Test with simple values that won't be tagged
        test_tuple = (1, "hello", 3.14)
        result = tag_tuple.to_json(test_tuple)
        
        # Verify the result is a list with the same items
        # (since simple types won't be tagged by default serializer)
        assert result == [1, "hello", 3.14]
        assert isinstance(result, list)
        
    def test_to_python_converts_to_tuple(self):
        """Test that to_python converts any iterable to tuple."""
        serializer = TaggedJSONSerializer()
        tag_tuple = TagTuple(serializer)
        
        # Test with list
        result = tag_tuple.to_python([1, 2, 3])
        assert result == (1, 2, 3)
        assert isinstance(result, tuple)
        
        # Test with tuple (should remain tuple)
        result = tag_tuple.to_python((4, 5, 6))
        assert result == (4, 5, 6)
        assert isinstance(result, tuple)
        
        # Test with generator
        def gen():
            yield 7
            yield 8
            yield 9
            
        result = tag_tuple.to_python(gen())
        assert result == (7, 8, 9)
        assert isinstance(result, tuple)
