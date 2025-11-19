# file: src/flask/src/flask/json/__init__.py:47-74
# asked: {"lines": [47, 70, 71, 73, 74], "branches": [[70, 71], [70, 73]]}
# gained: {"lines": [47, 70, 71, 73, 74], "branches": [[70, 71], [70, 73]]}

import pytest
import json
import tempfile
import os
from io import StringIO
from unittest.mock import Mock, patch

class TestFlaskJsonDump:
    
    def test_dump_with_current_app(self, monkeypatch):
        """Test dump when current_app is available"""
        mock_app = Mock()
        mock_json = Mock()
        mock_app.json = mock_json
        mock_app.json.dump = Mock()
        
        obj = {"test": "data"}
        fp = StringIO()
        
        with patch('flask.json.current_app', mock_app):
            from flask.json import dump
            dump(obj, fp, indent=2)
        
        mock_app.json.dump.assert_called_once_with(obj, fp, indent=2)
    
    def test_dump_without_current_app(self, monkeypatch):
        """Test dump when current_app is not available"""
        obj = {"test": "data"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fp:
            try:
                with patch('flask.json.current_app', None):
                    from flask.json import dump
                    dump(obj, fp, indent=2)
                
                fp.flush()
                
                with open(fp.name, 'r') as f:
                    content = json.load(f)
                
                assert content == obj
            finally:
                os.unlink(fp.name)
    
    def test_dump_without_current_app_custom_default(self, monkeypatch):
        """Test dump when current_app is not available with custom default function"""
        obj = {"test": "data"}
        
        def custom_default(o):
            if isinstance(o, set):
                return list(o)
            raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fp:
            try:
                with patch('flask.json.current_app', None):
                    from flask.json import dump
                    dump(obj, fp, default=custom_default, indent=2)
                
                fp.flush()
                
                with open(fp.name, 'r') as f:
                    content = json.load(f)
                
                assert content == obj
            finally:
                os.unlink(fp.name)
    
    def test_dump_without_current_app_uses_flask_default(self, monkeypatch):
        """Test that dump uses flask's _default when no current_app and no custom default"""
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        obj = {"custom": CustomObject("test")}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fp:
            try:
                with patch('flask.json.current_app', None):
                    from flask.json import dump
                    
                    with pytest.raises(TypeError):
                        dump(obj, fp)
            finally:
                os.unlink(fp.name)
