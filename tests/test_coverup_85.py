# file: src/flask/src/flask/wrappers.py:92-113
# asked: {"lines": [92, 93, 107, 108, 110, 111, 113], "branches": [[107, 108], [107, 110], [110, 111], [110, 113]]}
# gained: {"lines": [92, 93, 107, 108, 110, 111, 113], "branches": [[107, 108], [107, 110], [110, 111], [110, 113]]}

import pytest
from flask import Flask
from flask.wrappers import Request
from werkzeug.test import EnvironBuilder


class TestRequestMaxFormMemorySize:
    """Test cases for Request.max_form_memory_size property."""
    
    def test_max_form_memory_size_instance_override(self):
        """Test that instance-level _max_form_memory_size takes precedence."""
        builder = EnvironBuilder()
        env = builder.get_environ()
        request = Request(env)
        
        # Set instance-level override
        request._max_form_memory_size = 100000
        
        # Should return the instance-level value
        assert request.max_form_memory_size == 100000
    
    def test_max_form_memory_size_with_current_app(self, monkeypatch):
        """Test that current_app.config is used when current_app exists."""
        app = Flask(__name__)
        app.config['MAX_FORM_MEMORY_SIZE'] = 750000
        
        builder = EnvironBuilder()
        env = builder.get_environ()
        
        with app.test_request_context():
            request = Request(env)
            # Should return the app config value
            assert request.max_form_memory_size == 750000
    
    def test_max_form_memory_size_without_current_app(self, monkeypatch):
        """Test that super().max_form_memory_size is used when no current_app."""
        builder = EnvironBuilder()
        env = builder.get_environ()
        request = Request(env)
        
        # Mock current_app to be None
        monkeypatch.setattr('flask.wrappers.current_app', None)
        
        # Should call parent class implementation
        parent_value = super(Request, request).max_form_memory_size
        assert request.max_form_memory_size == parent_value
    
    def test_max_form_memory_size_app_default(self):
        """Test default behavior when no instance override and current_app exists."""
        app = Flask(__name__)
        # Don't set MAX_FORM_MEMORY_SIZE, should use default
        
        builder = EnvironBuilder()
        env = builder.get_environ()
        
        with app.test_request_context():
            request = Request(env)
            # Should return default value from app config
            assert request.max_form_memory_size == 500000
