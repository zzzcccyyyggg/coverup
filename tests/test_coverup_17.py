# file: src/flask/src/flask/json/provider.py:108-121
# asked: {"lines": [108, 109, 110, 112, 113, 115, 116, 118, 119, 121], "branches": [[109, 110], [109, 112], [112, 113], [112, 115], [115, 116], [115, 118], [118, 119], [118, 121]]}
# gained: {"lines": [108, 109, 110, 112, 113, 115, 116, 118, 119, 121], "branches": [[109, 110], [109, 112], [112, 113], [112, 115], [115, 116], [115, 118], [118, 119], [118, 121]]}

import pytest
import dataclasses
import decimal
import uuid
from datetime import date
from werkzeug.http import http_date
from flask.json.provider import _default


class TestDefaultFunction:
    """Test cases for the _default function in flask.json.provider"""
    
    def test_date_object(self):
        """Test that date objects are converted to HTTP date format"""
        test_date = date(2023, 12, 25)
        result = _default(test_date)
        expected = http_date(test_date)
        assert result == expected
    
    def test_decimal_object(self):
        """Test that decimal.Decimal objects are converted to string"""
        test_decimal = decimal.Decimal("123.45")
        result = _default(test_decimal)
        assert result == "123.45"
    
    def test_uuid_object(self):
        """Test that UUID objects are converted to string"""
        test_uuid = uuid.uuid4()
        result = _default(test_uuid)
        assert result == str(test_uuid)
    
    def test_dataclass_object(self):
        """Test that dataclass objects are converted to dict"""
        @dataclasses.dataclass
        class TestDataClass:
            name: str
            value: int
        
        test_obj = TestDataClass(name="test", value=42)
        result = _default(test_obj)
        expected = {"name": "test", "value": 42}
        assert result == expected
    
    def test_object_with_html_method(self):
        """Test that objects with __html__ method are converted using that method"""
        class HTMLObject:
            def __html__(self):
                return "<div>test</div>"
        
        test_obj = HTMLObject()
        result = _default(test_obj)
        assert result == "<div>test</div>"
    
    def test_unsupported_object_raises_typeerror(self):
        """Test that unsupported objects raise TypeError"""
        class UnsupportedObject:
            pass
        
        test_obj = UnsupportedObject()
        with pytest.raises(TypeError) as exc_info:
            _default(test_obj)
        
        assert f"Object of type {type(test_obj).__name__} is not JSON serializable" in str(exc_info.value)
