# file: src/flask/src/flask/json/provider.py:181-187
# asked: {"lines": [181, 187], "branches": []}
# gained: {"lines": [181, 187], "branches": []}

import pytest
import json
from flask import Flask
from flask.json.provider import DefaultJSONProvider

class TestDefaultJSONProviderLoads:
    """Test cases for DefaultJSONProvider.loads method."""
    
    def test_loads_with_string(self):
        """Test loads method with string input."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        test_data = '{"key": "value", "number": 42}'
        result = provider.loads(test_data)
        expected = {"key": "value", "number": 42}
        assert result == expected
    
    def test_loads_with_bytes(self):
        """Test loads method with bytes input."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        test_data = b'{"key": "value", "number": 42}'
        result = provider.loads(test_data)
        expected = {"key": "value", "number": 42}
        assert result == expected
    
    def test_loads_with_kwargs(self):
        """Test loads method with additional kwargs."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        test_data = '{"key": "value", "number": 42}'
        result = provider.loads(test_data, parse_float=float)
        expected = {"key": "value", "number": 42}
        assert result == expected
    
    def test_loads_with_empty_string(self):
        """Test loads method with empty string."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        test_data = ''
        with pytest.raises(json.JSONDecodeError):
            provider.loads(test_data)
    
    def test_loads_with_invalid_json(self):
        """Test loads method with invalid JSON string."""
        app = Flask(__name__)
        provider = DefaultJSONProvider(app)
        test_data = 'invalid json'
        with pytest.raises(json.JSONDecodeError):
            provider.loads(test_data)
