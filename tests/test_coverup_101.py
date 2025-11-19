# file: src/flask/src/flask/json/provider.py:189-215
# asked: {"lines": [189, 205, 206, 208, 209, 211, 213, 214], "branches": [[208, 209], [208, 211]]}
# gained: {"lines": [189, 205, 206, 208, 209, 211, 213, 214], "branches": [[208, 209], [208, 211]]}

import pytest
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from werkzeug.sansio.response import Response


class TestDefaultJSONProviderResponse:
    """Test cases for DefaultJSONProvider.response method to achieve full coverage."""
    
    def test_response_with_compact_none_and_debug_true(self, monkeypatch):
        """Test response when compact is None and app.debug is True."""
        app = Flask(__name__)
        app.debug = True
        provider = DefaultJSONProvider(app)
        provider.compact = None
        
        # Mock dumps to avoid actual JSON serialization
        def mock_dumps(obj, **kwargs):
            assert "indent" in kwargs
            assert kwargs["indent"] == 2
            return "test"
        
        monkeypatch.setattr(provider, "dumps", mock_dumps)
        
        result = provider.response("test_data")
        assert isinstance(result, Response)
        assert result.mimetype == "application/json"
        assert result.get_data(as_text=True) == "test\n"
    
    def test_response_with_compact_false(self):
        """Test response when compact is explicitly False."""
        app = Flask(__name__)
        app.debug = False  # Ensure debug is False to test compact=False path
        provider = DefaultJSONProvider(app)
        provider.compact = False
        
        # Mock dumps to verify indent is used
        def mock_dumps(obj, **kwargs):
            assert "indent" in kwargs
            assert kwargs["indent"] == 2
            return "formatted"
        
        provider.dumps = mock_dumps
        
        result = provider.response({"key": "value"})
        assert isinstance(result, Response)
        assert result.mimetype == "application/json"
    
    def test_response_with_compact_true(self):
        """Test response when compact is True."""
        app = Flask(__name__)
        app.debug = True  # Even with debug True, compact=True should use separators
        provider = DefaultJSONProvider(app)
        provider.compact = True
        
        # Mock dumps to verify separators are used
        def mock_dumps(obj, **kwargs):
            assert "separators" in kwargs
            assert kwargs["separators"] == (",", ":")
            return "compact"
        
        provider.dumps = mock_dumps
        
        result = provider.response(data="value")
        assert isinstance(result, Response)
        assert result.mimetype == "application/json"
        assert result.get_data(as_text=True) == "compact\n"
    
    def test_response_with_compact_none_and_debug_false(self):
        """Test response when compact is None and app.debug is False."""
        app = Flask(__name__)
        app.debug = False
        provider = DefaultJSONProvider(app)
        provider.compact = None
        
        # Mock dumps to verify separators are used
        def mock_dumps(obj, **kwargs):
            assert "separators" in kwargs
            assert kwargs["separators"] == (",", ":")
            return "non_debug"
        
        provider.dumps = mock_dumps
        
        result = provider.response([1, 2, 3])
        assert isinstance(result, Response)
        assert result.mimetype == "application/json"
        assert result.get_data(as_text=True) == "non_debug\n"
