# file: src/flask/src/flask/wrappers.py:59-86
# asked: {"lines": [59, 60, 80, 81, 83, 84, 86], "branches": [[80, 81], [80, 83], [83, 84], [83, 86]]}
# gained: {"lines": [59, 60, 80, 81, 83, 84, 86], "branches": [[80, 81], [80, 83], [83, 84], [83, 86]]}

import pytest
from flask import Flask
from flask.wrappers import Request
from werkzeug.test import EnvironBuilder


class TestRequestMaxContentLength:
    """Test cases for Request.max_content_length property."""
    
    def test_max_content_length_when_set_per_request(self):
        """Test max_content_length when _max_content_length is set on the request."""
        builder = EnvironBuilder()
        env = builder.get_environ()
        request = Request(env)
        request._max_content_length = 1024
        
        assert request.max_content_length == 1024
    
    def test_max_content_length_without_current_app(self, monkeypatch):
        """Test max_content_length when current_app is None."""
        builder = EnvironBuilder()
        env = builder.get_environ()
        request = Request(env)
        
        # Mock current_app to be None
        monkeypatch.setattr('flask.wrappers.current_app', None)
        
        # Should call parent class implementation
        result = request.max_content_length
        assert result is None  # Default Werkzeug behavior
    
    def test_max_content_length_from_app_config(self):
        """Test max_content_length when using app config."""
        app = Flask(__name__)
        app.config['MAX_CONTENT_LENGTH'] = 2048
        
        with app.test_request_context():
            builder = EnvironBuilder()
            env = builder.get_environ()
            request = Request(env)
            
            assert request.max_content_length == 2048
    
    def test_max_content_length_none_from_app_config(self):
        """Test max_content_length when app config has MAX_CONTENT_LENGTH as None."""
        app = Flask(__name__)
        app.config['MAX_CONTENT_LENGTH'] = None
        
        with app.test_request_context():
            builder = EnvironBuilder()
            env = builder.get_environ()
            request = Request(env)
            
            assert request.max_content_length is None
