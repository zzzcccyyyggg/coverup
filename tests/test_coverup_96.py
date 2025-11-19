# file: src/flask/src/flask/json/tag.py:173-188
# asked: {"lines": [173, 174, 178, 179, 181, 182, 184, 185, 187, 188], "branches": []}
# gained: {"lines": [173, 174, 178, 179, 181, 182, 184, 185, 187, 188], "branches": []}

import pytest
from markupsafe import Markup
from flask.json.tag import TagMarkup, TaggedJSONSerializer


class TestTagMarkup:
    """Test cases for TagMarkup class to achieve full coverage."""
    
    def test_check_with_valid_markup_object(self):
        """Test check method with object having __html__ method."""
        serializer = TaggedJSONSerializer()
        tag_markup = TagMarkup(serializer)
        
        class MockMarkup:
            def __html__(self):
                return "<div>test</div>"
        
        assert tag_markup.check(MockMarkup()) is True
    
    def test_check_with_invalid_object_no_html_method(self):
        """Test check method with object without __html__ method."""
        serializer = TaggedJSONSerializer()
        tag_markup = TagMarkup(serializer)
        
        class NoMarkup:
            pass
        
        assert tag_markup.check(NoMarkup()) is False
    
    def test_check_with_object_html_not_callable(self):
        """Test check method with object having non-callable __html__ attribute."""
        serializer = TaggedJSONSerializer()
        tag_markup = TagMarkup(serializer)
        
        class NonCallableMarkup:
            __html__ = "not callable"
        
        assert tag_markup.check(NonCallableMarkup()) is False
    
    def test_to_json_with_markup_object(self):
        """Test to_json method with markup object."""
        serializer = TaggedJSONSerializer()
        tag_markup = TagMarkup(serializer)
        
        class MockMarkup:
            def __html__(self):
                return "<div>test content</div>"
        
        markup_obj = MockMarkup()
        result = tag_markup.to_json(markup_obj)
        
        assert result == "<div>test content</div>"
    
    def test_to_python_with_string_value(self):
        """Test to_python method with string value."""
        serializer = TaggedJSONSerializer()
        tag_markup = TagMarkup(serializer)
        
        result = tag_markup.to_python("<p>test paragraph</p>")
        
        assert isinstance(result, Markup)
        assert str(result) == "<p>test paragraph</p>"
    
    def test_to_python_with_empty_string(self):
        """Test to_python method with empty string."""
        serializer = TaggedJSONSerializer()
        tag_markup = TagMarkup(serializer)
        
        result = tag_markup.to_python("")
        
        assert isinstance(result, Markup)
        assert str(result) == ""
