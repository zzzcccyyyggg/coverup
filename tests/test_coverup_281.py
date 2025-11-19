# file: src/flask/src/flask/json/provider.py:67-73
# asked: {"lines": [67, 73], "branches": []}
# gained: {"lines": [67, 73], "branches": []}

import pytest
import io
from flask import Flask
from flask.json.provider import JSONProvider

class TestJSONProviderLoad:
    """Test cases for JSONProvider.load method to achieve full coverage."""
    
    def test_load_with_text_file(self, monkeypatch):
        """Test JSONProvider.load with a text file."""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        # Create a mock text file with JSON content
        json_content = '{"key": "value", "number": 42}'
        fp = io.StringIO(json_content)
        
        # Mock loads to return expected data
        def mock_loads(s, **kwargs):
            return {"key": "value", "number": 42}
        
        monkeypatch.setattr(provider, 'loads', mock_loads)
        
        # Call the load method
        result = provider.load(fp)
        
        # Verify the result matches expected JSON
        assert result == {"key": "value", "number": 42}
    
    def test_load_with_bytes_file(self, monkeypatch):
        """Test JSONProvider.load with a bytes file."""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        # Create a mock bytes file with JSON content
        json_content = b'{"key": "value", "number": 42}'
        fp = io.BytesIO(json_content)
        
        # Mock loads to return expected data
        def mock_loads(s, **kwargs):
            return {"key": "value", "number": 42}
        
        monkeypatch.setattr(provider, 'loads', mock_loads)
        
        # Call the load method
        result = provider.load(fp)
        
        # Verify the result matches expected JSON
        assert result == {"key": "value", "number": 42}
    
    def test_load_with_kwargs(self, monkeypatch):
        """Test JSONProvider.load with additional kwargs."""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        # Create a mock text file with JSON content
        json_content = '{"key": "value", "number": 42}'
        fp = io.StringIO(json_content)
        
        # Mock loads to return expected data and track kwargs
        captured_kwargs = {}
        
        def mock_loads(s, **kwargs):
            captured_kwargs.update(kwargs)
            return {"key": "value", "number": 42}
        
        monkeypatch.setattr(provider, 'loads', mock_loads)
        
        # Call the load method with kwargs
        result = provider.load(fp, parse_float=float, parse_int=int)
        
        # Verify the result matches expected JSON and kwargs were passed
        assert result == {"key": "value", "number": 42}
        assert captured_kwargs == {"parse_float": float, "parse_int": int}
    
    def test_load_calls_loads_with_file_content(self, monkeypatch):
        """Test that load calls loads with the file content."""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        # Create a mock text file with JSON content
        json_content = '{"test": "data"}'
        fp = io.StringIO(json_content)
        
        # Track calls to loads
        loads_calls = []
        
        def mock_loads(s, **kwargs):
            loads_calls.append((s, kwargs))
            return {"test": "data"}
        
        monkeypatch.setattr(provider, 'loads', mock_loads)
        
        # Call the load method
        result = provider.load(fp, custom_kwarg="test")
        
        # Verify loads was called with the file content and kwargs
        assert len(loads_calls) == 1
        assert loads_calls[0][0] == json_content
        assert loads_calls[0][1] == {"custom_kwarg": "test"}
        assert result == {"test": "data"}
