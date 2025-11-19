# file: src/flask/src/flask/json/tag.py:249-254
# asked: {"lines": [249, 250, 251, 253, 254], "branches": [[253, 0], [253, 254]]}
# gained: {"lines": [249, 250, 251, 253, 254], "branches": [[253, 0], [253, 254]]}

import pytest
from flask.json.tag import TaggedJSONSerializer, JSONTag


class TestTaggedJSONSerializerInit:
    """Test cases for TaggedJSONSerializer.__init__ method."""
    
    def test_init_registers_default_tags(self):
        """Test that __init__ registers all default tags."""
        serializer = TaggedJSONSerializer()
        
        # Verify that all default tags are registered
        assert len(serializer.order) == len(TaggedJSONSerializer.default_tags)
        assert len(serializer.tags) == len([tag for tag in TaggedJSONSerializer.default_tags if tag.key])
        
        # Verify that the order list contains instances of the tag classes
        for tag_instance in serializer.order:
            assert isinstance(tag_instance, JSONTag)
            
        # Verify that tags dict contains the expected keys
        expected_keys = []
        for tag_class in TaggedJSONSerializer.default_tags:
            # Create a temporary instance to get the key
            temp_tag = tag_class(serializer)
            if temp_tag.key:
                expected_keys.append(temp_tag.key)
                assert temp_tag.key in serializer.tags
                assert isinstance(serializer.tags[temp_tag.key], JSONTag)
