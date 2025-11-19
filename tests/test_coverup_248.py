# file: src/flask/src/flask/testing.py:88-94
# asked: {"lines": [88, 94], "branches": []}
# gained: {"lines": [88, 94], "branches": []}

import pytest
import typing as t
from flask import Flask
from flask.testing import EnvironBuilder


class TestEnvironBuilderJsonDumps:
    """Test cases for EnvironBuilder.json_dumps method."""
    
    def test_json_dumps_calls_app_json_dumps(self):
        """Test that json_dumps calls the app's json.dumps method."""
        app = Flask(__name__)
        
        # Mock the app's json.dumps method to track calls
        mock_dumps_called = False
        mock_dumps_args = None
        mock_dumps_kwargs = None
        
        def mock_dumps(obj: t.Any, **kwargs: t.Any) -> str:
            nonlocal mock_dumps_called, mock_dumps_args, mock_dumps_kwargs
            mock_dumps_called = True
            mock_dumps_args = obj
            mock_dumps_kwargs = kwargs
            return '{"test": "data"}'
        
        app.json.dumps = mock_dumps
        
        builder = EnvironBuilder(app, '/')
        test_obj = {'key': 'value'}
        result = builder.json_dumps(test_obj, indent=2)
        
        # Verify the method was called with correct arguments
        assert mock_dumps_called
        assert mock_dumps_args == test_obj
        assert mock_dumps_kwargs == {'indent': 2}
        assert result == '{"test": "data"}'
    
    def test_json_dumps_with_no_kwargs(self):
        """Test json_dumps with no additional keyword arguments."""
        app = Flask(__name__)
        
        # Mock the app's json.dumps method
        def mock_dumps(obj: t.Any, **kwargs: t.Any) -> str:
            assert obj == {'simple': 'object'}
            assert kwargs == {}
            return '{"simple": "object"}'
        
        app.json.dumps = mock_dumps
        
        builder = EnvironBuilder(app, '/')
        result = builder.json_dumps({'simple': 'object'})
        
        assert result == '{"simple": "object"}'
    
    def test_json_dumps_with_multiple_kwargs(self):
        """Test json_dumps with multiple keyword arguments."""
        app = Flask(__name__)
        
        # Mock the app's json.dumps method
        def mock_dumps(obj: t.Any, **kwargs: t.Any) -> str:
            assert obj == {'complex': 'data'}
            assert kwargs == {'indent': 4, 'sort_keys': True, 'separators': (',', ':')}
            return '{"complex": "data"}'
        
        app.json.dumps = mock_dumps
        
        builder = EnvironBuilder(app, '/')
        result = builder.json_dumps(
            {'complex': 'data'}, 
            indent=4, 
            sort_keys=True, 
            separators=(',', ':')
        )
        
        assert result == '{"complex": "data"}'
