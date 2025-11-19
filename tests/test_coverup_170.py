# file: src/flask/src/flask/json/provider.py:166-179
# asked: {"lines": [166, 176, 177, 178, 179], "branches": []}
# gained: {"lines": [166, 176, 177, 178, 179], "branches": []}

import pytest
import json
from flask import Flask
from flask.json.provider import DefaultJSONProvider

class TestDefaultJSONProviderDumps:
    """Test cases for DefaultJSONProvider.dumps method to cover lines 166-179."""
    
    def test_dumps_with_default_kwargs(self):
        """Test that dumps uses the provider's default, ensure_ascii, and sort_keys attributes."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        
        # Test data that will use the default handler
        test_obj = {"test": "value", "number": 42}
        
        # Call dumps without any kwargs - should use provider's defaults
        result = provider.dumps(test_obj)
        
        # Verify the result is valid JSON
        parsed = json.loads(result)
        assert parsed == test_obj
        
        # Verify the default kwargs were applied by checking the serialization format
        # With ensure_ascii=True and sort_keys=True, keys should be sorted and ASCII-only
        assert '"number": 42' in result
        assert '"test": "value"' in result
        # Keys should be sorted: "number" comes before "test"
        assert result.index('"number"') < result.index('"test"')
    
    def test_dumps_with_custom_kwargs_override(self):
        """Test that custom kwargs override the provider's default attributes."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        
        test_obj = {"b": 2, "a": 1}
        
        # Override the provider's defaults with custom kwargs
        result = provider.dumps(test_obj, sort_keys=False, ensure_ascii=False)
        
        # With sort_keys=False, original order should be preserved
        parsed = json.loads(result)
        assert parsed == test_obj
        # Keys should be in original order: "b" before "a"
        assert result.index('"b"') < result.index('"a"')
    
    def test_dumps_with_custom_default_handler(self):
        """Test that custom default handler in kwargs overrides provider's default."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        
        # Create an object that will trigger the default handler
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        test_obj = CustomObject("test")
        
        # Use a custom default handler that converts our custom object
        def custom_default(obj):
            if isinstance(obj, CustomObject):
                return {"custom_value": obj.value}
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        result = provider.dumps(test_obj, default=custom_default)
        
        # Verify the custom default handler was used
        parsed = json.loads(result)
        assert parsed == {"custom_value": "test"}
    
    def test_dumps_with_partial_kwargs(self):
        """Test that only provided kwargs override defaults, others use provider attributes."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        
        test_obj = {"z": 3, "y": 2, "x": 1}
        
        # Only override ensure_ascii, sort_keys should still use provider default (True)
        result = provider.dumps(test_obj, ensure_ascii=False)
        
        parsed = json.loads(result)
        assert parsed == test_obj
        # With sort_keys=True (provider default), keys should be sorted: "x", "y", "z"
        assert result.index('"x"') < result.index('"y"') < result.index('"z"')
