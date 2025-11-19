# file: src/flask/src/flask/json/__init__.py:108-135
# asked: {"lines": [108, 132, 133, 135], "branches": [[132, 133], [132, 135]]}
# gained: {"lines": [108, 132, 133, 135], "branches": [[132, 133], [132, 135]]}

import pytest
import json
import tempfile
import os
from io import StringIO, BytesIO
from unittest.mock import Mock, patch
import flask.json

def test_load_with_current_app():
    """Test flask.json.load when current_app is available."""
    mock_app = Mock()
    mock_json_provider = Mock()
    mock_app.json = mock_json_provider
    mock_json_provider.load.return_value = {"test": "data"}
    
    test_data = '{"test": "data"}'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(test_data)
        temp_path = f.name
    
    try:
        with open(temp_path, 'r') as fp:
            with patch('flask.json.current_app', mock_app):
                result = flask.json.load(fp)
                mock_json_provider.load.assert_called_once_with(fp)
                assert result == {"test": "data"}
    finally:
        os.unlink(temp_path)

def test_load_without_current_app():
    """Test flask.json.load when current_app is not available."""
    test_data = '{"test": "data"}'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(test_data)
        temp_path = f.name
    
    try:
        with open(temp_path, 'r') as fp:
            with patch('flask.json.current_app', None):
                result = flask.json.load(fp)
                assert result == {"test": "data"}
    finally:
        os.unlink(temp_path)

def test_load_with_kwargs_with_current_app():
    """Test flask.json.load with kwargs when current_app is available."""
    mock_app = Mock()
    mock_json_provider = Mock()
    mock_app.json = mock_json_provider
    mock_json_provider.load.return_value = {"test": "data"}
    
    test_data = '{"test": "data"}'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(test_data)
        temp_path = f.name
    
    try:
        with open(temp_path, 'r') as fp:
            with patch('flask.json.current_app', mock_app):
                result = flask.json.load(fp, parse_float=float)
                mock_json_provider.load.assert_called_once_with(fp, parse_float=float)
                assert result == {"test": "data"}
    finally:
        os.unlink(temp_path)

def test_load_with_kwargs_without_current_app():
    """Test flask.json.load with kwargs when current_app is not available."""
    test_data = '{"test": "data"}'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(test_data)
        temp_path = f.name
    
    try:
        with open(temp_path, 'r') as fp:
            with patch('flask.json.current_app', None):
                result = flask.json.load(fp, parse_float=float)
                assert result == {"test": "data"}
    finally:
        os.unlink(temp_path)
