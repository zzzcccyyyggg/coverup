# file: src/flask/src/flask/json/tag.py:191-202
# asked: {"lines": [191, 192, 193, 195, 196, 198, 199, 201, 202], "branches": []}
# gained: {"lines": [191, 192, 193, 195, 196, 198, 199, 201, 202], "branches": []}

import pytest
import typing as t
from uuid import UUID
from flask.json.tag import TagUUID, TaggedJSONSerializer


class TestTagUUID:
    """Test cases for TagUUID class to achieve full coverage."""
    
    def test_check_with_uuid_returns_true(self):
        """Test that check returns True for UUID instances."""
        serializer = TaggedJSONSerializer()
        tag_uuid = TagUUID(serializer)
        uuid_obj = UUID('12345678-1234-5678-1234-567812345678')
        
        result = tag_uuid.check(uuid_obj)
        
        assert result is True
    
    def test_check_with_non_uuid_returns_false(self):
        """Test that check returns False for non-UUID values."""
        serializer = TaggedJSONSerializer()
        tag_uuid = TagUUID(serializer)
        
        # Test with string
        result = tag_uuid.check("not-a-uuid")
        assert result is False
        
        # Test with integer
        result = tag_uuid.check(123)
        assert result is False
        
        # Test with None
        result = tag_uuid.check(None)
        assert result is False
    
    def test_to_json_converts_uuid_to_hex(self):
        """Test that to_json converts UUID to hex string."""
        serializer = TaggedJSONSerializer()
        tag_uuid = TagUUID(serializer)
        uuid_obj = UUID('12345678-1234-5678-1234-567812345678')
        
        result = tag_uuid.to_json(uuid_obj)
        
        assert result == '12345678123456781234567812345678'
        assert isinstance(result, str)
    
    def test_to_python_converts_hex_to_uuid(self):
        """Test that to_python converts hex string to UUID."""
        serializer = TaggedJSONSerializer()
        tag_uuid = TagUUID(serializer)
        hex_string = '12345678123456781234567812345678'
        
        result = tag_uuid.to_python(hex_string)
        
        assert isinstance(result, UUID)
        assert str(result) == '12345678-1234-5678-1234-567812345678'
        assert result.hex == hex_string
