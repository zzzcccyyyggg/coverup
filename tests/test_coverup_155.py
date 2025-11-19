# file: src/flask/src/flask/json/__init__.py:77-105
# asked: {"lines": [77, 102, 103, 105], "branches": [[102, 103], [102, 105]]}
# gained: {"lines": [77, 102, 103, 105], "branches": [[102, 103], [102, 105]]}

import pytest
import json
from flask import Flask
from flask.json import loads


def test_loads_without_app_context():
    """Test loads function when no app context is available."""
    # Test with string input
    result = loads('{"key": "value"}')
    assert result == {"key": "value"}
    
    # Test with bytes input
    result = loads(b'{"key": "value"}')
    assert result == {"key": "value"}
    
    # Test with additional kwargs
    result = loads('{"key": "value"}', parse_float=float)
    assert result == {"key": "value"}


def test_loads_with_app_context(monkeypatch):
    """Test loads function when app context is available."""
    app = Flask(__name__)
    
    # Mock the app's json.loads method
    mock_loads_calls = []
    def mock_loads(s, **kwargs):
        mock_loads_calls.append((s, kwargs))
        return {"mocked": True, "data": s}
    
    monkeypatch.setattr(app.json, 'loads', mock_loads)
    
    with app.app_context():
        # Test with string input
        result = loads('{"key": "value"}')
        assert result == {"mocked": True, "data": '{"key": "value"}'}
        assert len(mock_loads_calls) == 1
        assert mock_loads_calls[0][0] == '{"key": "value"}'
        
        # Test with bytes input
        result = loads(b'{"key": "value"}')
        assert result == {"mocked": True, "data": b'{"key": "value"}'}
        assert len(mock_loads_calls) == 2
        assert mock_loads_calls[1][0] == b'{"key": "value"}'
        
        # Test with additional kwargs
        result = loads('{"key": "value"}', parse_int=int)
        assert result == {"mocked": True, "data": '{"key": "value"}'}
        assert len(mock_loads_calls) == 3
        assert mock_loads_calls[2][1] == {'parse_int': int}
