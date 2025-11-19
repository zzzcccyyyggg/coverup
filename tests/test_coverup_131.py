# file: src/flask/src/flask/json/tag.py:309-319
# asked: {"lines": [309, 310, 312, 314, 315, 317, 319], "branches": [[310, 312], [310, 315], [315, 317], [315, 319]]}
# gained: {"lines": [309, 310, 312, 314, 315, 317, 319], "branches": [[310, 312], [310, 315], [315, 317], [315, 319]]}

import pytest
import typing as t
from flask.json.tag import TaggedJSONSerializer


class TestTaggedJSONSerializer:
    def test_untag_scan_with_dict_containing_tagged_value(self):
        """Test _untag_scan with a dict that contains a tagged value that gets processed by untag."""
        serializer = TaggedJSONSerializer()
        
        # Test with a dict that should trigger the untag call
        test_dict = {"key": "value"}
        result = serializer._untag_scan(test_dict)
        
        # The dict should be returned as-is since untag will process it
        assert result == test_dict

    def test_untag_scan_with_list_containing_dicts(self):
        """Test _untag_scan with a list containing dicts that should be recursively processed."""
        serializer = TaggedJSONSerializer()
        
        # Create a list with a dict that should trigger the dict processing path
        test_list = [{"nested_key": "nested_value"}]
        result = serializer._untag_scan(test_list)
        
        # The list should be returned with the nested dict processed
        assert result == test_list

    def test_untag_scan_with_nested_structure(self):
        """Test _untag_scan with a complex nested structure."""
        serializer = TaggedJSONSerializer()
        
        # Create a nested structure: list containing dict containing list
        test_data = [
            {
                "dict_key": ["list_item_1", "list_item_2"]
            }
        ]
        result = serializer._untag_scan(test_data)
        
        # Should return the same structure (untag won't modify in default case)
        assert result == test_data

    def test_untag_scan_with_empty_dict(self):
        """Test _untag_scan with an empty dict."""
        serializer = TaggedJSONSerializer()
        
        test_dict = {}
        result = serializer._untag_scan(test_dict)
        
        # Empty dict should be returned as-is
        assert result == test_dict

    def test_untag_scan_with_empty_list(self):
        """Test _untag_scan with an empty list."""
        serializer = TaggedJSONSerializer()
        
        test_list = []
        result = serializer._untag_scan(test_list)
        
        # Empty list should be returned as-is
        assert result == test_list

    def test_untag_scan_with_simple_value(self):
        """Test _untag_scan with a simple non-dict, non-list value."""
        serializer = TaggedJSONSerializer()
        
        test_value = "simple_string"
        result = serializer._untag_scan(test_value)
        
        # Simple value should be returned as-is
        assert result == test_value

    def test_untag_scan_with_none_value(self):
        """Test _untag_scan with None value."""
        serializer = TaggedJSONSerializer()
        
        test_value = None
        result = serializer._untag_scan(test_value)
        
        # None should be returned as-is
        assert result is None
