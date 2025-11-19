# file: src/flask/src/flask/json/tag.py:256-287
# asked: {"lines": [256, 259, 260, 275, 276, 278, 279, 280, 282, 284, 285, 287], "branches": [[278, 279], [278, 284], [279, 280], [279, 282], [284, 285], [284, 287]]}
# gained: {"lines": [256, 259, 260, 275, 276, 278, 279, 280, 282, 284, 285, 287], "branches": [[278, 279], [278, 284], [279, 280], [279, 282], [284, 285], [284, 287]]}

import pytest
from flask.json.tag import TaggedJSONSerializer, JSONTag


class TestTaggedJSONSerializerRegister:
    """Test cases for TaggedJSONSerializer.register method to cover lines 256-287."""
    
    def test_register_with_key_force_false_already_registered(self):
        """Test register with existing key and force=False raises KeyError."""
        serializer = TaggedJSONSerializer()
        
        class TestTag1(JSONTag):
            key = "test_tag"
            
        class TestTag2(JSONTag):
            key = "test_tag"
        
        # Register first tag
        serializer.register(TestTag1)
        
        # Try to register second tag with same key, should raise KeyError
        with pytest.raises(KeyError, match="Tag 'test_tag' is already registered."):
            serializer.register(TestTag2, force=False)
    
    def test_register_with_key_force_true_already_registered(self):
        """Test register with existing key and force=True overwrites."""
        serializer = TaggedJSONSerializer()
        
        class TestTag1(JSONTag):
            key = "test_tag"
            
        class TestTag2(JSONTag):
            key = "test_tag"
        
        # Register first tag
        serializer.register(TestTag1)
        
        # Register second tag with same key and force=True, should overwrite
        serializer.register(TestTag2, force=True)
        
        # Verify the tag was overwritten
        assert "test_tag" in serializer.tags
        assert isinstance(serializer.tags["test_tag"], TestTag2)
    
    def test_register_with_key_index_none(self):
        """Test register with key and index=None appends to end."""
        serializer = TaggedJSONSerializer()
        
        class TestTag(JSONTag):
            key = "test_tag"
        
        serializer.register(TestTag, index=None)
        
        # Verify tag is in tags dict and appended to order
        assert "test_tag" in serializer.tags
        assert len(serializer.order) == len(serializer.default_tags) + 1
        assert serializer.order[-1].key == "test_tag"
    
    def test_register_with_key_index_specified(self):
        """Test register with key and specific index inserts at position."""
        serializer = TaggedJSONSerializer()
        
        class TestTag(JSONTag):
            key = "test_tag"
        
        # Insert at beginning
        serializer.register(TestTag, index=0)
        
        # Verify tag is in tags dict and inserted at position 0
        assert "test_tag" in serializer.tags
        assert serializer.order[0].key == "test_tag"
    
    def test_register_with_empty_key(self):
        """Test register with empty key (line 278 condition false)."""
        serializer = TaggedJSONSerializer()
        
        class TestTag(JSONTag):
            key = ""  # Empty key
        
        serializer.register(TestTag)
        
        # Verify tag is NOT in tags dict but is in order
        assert "" not in serializer.tags
        assert len(serializer.order) == len(serializer.default_tags) + 1
        assert serializer.order[-1].key == ""
