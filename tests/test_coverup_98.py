# file: src/flask/src/flask/json/tag.py:159-170
# asked: {"lines": [159, 160, 161, 163, 164, 166, 167, 169, 170], "branches": []}
# gained: {"lines": [159, 160, 161, 163, 164, 166, 167, 169, 170], "branches": []}

import pytest
import typing as t
from base64 import b64decode, b64encode
from flask.json.tag import TagBytes, JSONTag


class TestTagBytes:
    """Test cases for TagBytes class to achieve full coverage."""
    
    def test_check_with_bytes_returns_true(self):
        """Test that check method returns True for bytes input."""
        tag_bytes = TagBytes(None)
        assert tag_bytes.check(b"test data") is True
        
    def test_check_with_non_bytes_returns_false(self):
        """Test that check method returns False for non-bytes input."""
        tag_bytes = TagBytes(None)
        assert tag_bytes.check("string data") is False
        assert tag_bytes.check(123) is False
        assert tag_bytes.check([1, 2, 3]) is False
        assert tag_bytes.check({"key": "value"}) is False
        
    def test_to_json_encodes_bytes_to_base64_string(self):
        """Test that to_json encodes bytes to base64 string."""
        tag_bytes = TagBytes(None)
        test_bytes = b"hello world"
        expected = b64encode(test_bytes).decode("ascii")
        result = tag_bytes.to_json(test_bytes)
        assert result == expected
        assert isinstance(result, str)
        
    def test_to_python_decodes_base64_string_to_bytes(self):
        """Test that to_python decodes base64 string back to bytes."""
        tag_bytes = TagBytes(None)
        test_string = b64encode(b"test data").decode("ascii")
        expected = b"test data"
        result = tag_bytes.to_python(test_string)
        assert result == expected
        assert isinstance(result, bytes)
