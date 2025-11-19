# file: src/flask/src/flask/json/__init__.py:13-44
# asked: {"lines": [13, 40, 41, 43, 44], "branches": [[40, 41], [40, 43]]}
# gained: {"lines": [13, 40, 41, 43, 44], "branches": [[40, 41], [40, 43]]}

import pytest
import json
import decimal
import uuid
from datetime import date
from flask import Flask
from flask.json import dumps
from flask.json.provider import _default

class TestJsonDumps:
    def test_dumps_without_current_app(self, monkeypatch):
        """Test dumps when current_app is None (lines 43-44)"""
        # Mock current_app to be None
        monkeypatch.setattr('flask.json.current_app', None)
        
        # Test with a simple object
        result = dumps({'test': 'value'})
        expected = json.dumps({'test': 'value'}, default=_default)
        assert result == expected
        
        # Test with a custom default function
        custom_default = lambda x: str(x) if isinstance(x, set) else None
        result = dumps({'set': {1, 2, 3}}, default=custom_default)
        expected = json.dumps({'set': {1, 2, 3}}, default=custom_default)
        assert result == expected

    def test_dumps_with_current_app(self):
        """Test dumps when current_app is available (lines 40-41)"""
        app = Flask(__name__)
        
        with app.app_context():
            # Mock the json.dumps method to verify it's called
            original_dumps = app.json.dumps
            called_with = []
            
            def mock_dumps(obj, **kwargs):
                called_with.append((obj, kwargs))
                return original_dumps(obj, **kwargs)
            
            app.json.dumps = mock_dumps
            
            # Test dumps call
            test_obj = {'key': 'value'}
            result = dumps(test_obj, indent=2)
            
            # Verify current_app.json.dumps was called with correct parameters
            assert len(called_with) == 1
            assert called_with[0][0] == test_obj
            assert called_with[0][1]['indent'] == 2
            
            # Verify the result is correct
            expected = original_dumps(test_obj, indent=2)
            assert result == expected

    def test_dumps_with_unsupported_types_without_current_app(self, monkeypatch):
        """Test dumps with unsupported types when current_app is None (line 43-44 with _default)"""
        monkeypatch.setattr('flask.json.current_app', None)
        
        # Test with decimal.Decimal (should be converted to string)
        dec_obj = decimal.Decimal('123.45')
        result = dumps(dec_obj)
        assert result == '"123.45"'
        
        # Test with UUID (should be converted to string)
        uuid_obj = uuid.uuid4()
        result = dumps(uuid_obj)
        assert result == f'"{str(uuid_obj)}"'
        
        # Test with date (should be converted to HTTP date string)
        date_obj = date(2023, 1, 1)
        result = dumps(date_obj)
        # The exact format depends on http_date implementation, but it should be a string
        assert isinstance(result, str)
        assert result.startswith('"') and result.endswith('"')

    def test_dumps_raises_type_error_without_current_app(self, monkeypatch):
        """Test that dumps raises TypeError for truly unsupported types when current_app is None"""
        monkeypatch.setattr('flask.json.current_app', None)
        
        # Test with a completely unsupported type
        class Unserializable:
            pass
        
        with pytest.raises(TypeError):
            dumps(Unserializable())
