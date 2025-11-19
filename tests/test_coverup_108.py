# file: src/flask/src/flask/helpers.py:628-635
# asked: {"lines": [628, 629, 630, 632, 633, 635], "branches": [[632, 633], [632, 635]]}
# gained: {"lines": [628, 629, 630, 632, 633, 635], "branches": [[632, 633], [632, 635]]}

import pytest
from flask.helpers import _split_blueprint_path


class TestSplitBlueprintPath:
    def test_single_component(self):
        """Test with a name that has no dots (single component)."""
        result = _split_blueprint_path("simple")
        assert result == ["simple"]
    
    def test_two_components(self):
        """Test with a name that has one dot (two components)."""
        result = _split_blueprint_path("parent.child")
        assert result == ["parent.child", "parent"]
    
    def test_three_components(self):
        """Test with a name that has two dots (three components)."""
        result = _split_blueprint_path("grand.parent.child")
        assert result == ["grand.parent.child", "grand.parent", "grand"]
    
    def test_multiple_calls_same_input(self):
        """Test that the cache decorator works correctly."""
        # First call
        result1 = _split_blueprint_path("a.b.c")
        # Second call with same input should use cache
        result2 = _split_blueprint_path("a.b.c")
        assert result1 == result2 == ["a.b.c", "a.b", "a"]
    
    def test_empty_string(self):
        """Test with empty string (edge case)."""
        result = _split_blueprint_path("")
        assert result == [""]
