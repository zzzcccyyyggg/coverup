# file: src/flask/src/flask/wrappers.py:119-140
# asked: {"lines": [119, 120, 134, 135, 137, 138, 140], "branches": [[134, 135], [134, 137], [137, 138], [137, 140]]}
# gained: {"lines": [119, 120, 134, 135, 137, 138, 140], "branches": [[134, 135], [134, 137], [137, 138], [137, 140]]}

import pytest
from flask import Flask
from flask.wrappers import Request
from werkzeug.test import EnvironBuilder


class TestRequestMaxFormParts:
    """Test cases for Request.max_form_parts property to achieve full coverage."""
    
    def test_max_form_parts_with_instance_value(self):
        """Test when _max_form_parts is set on the request instance."""
        builder = EnvironBuilder()
        env = builder.get_environ()
        request = Request(env)
        request._max_form_parts = 500
        
        result = request.max_form_parts
        
        assert result == 500
    
    def test_max_form_parts_without_current_app(self, monkeypatch):
        """Test when there is no current_app context."""
        builder = EnvironBuilder()
        env = builder.get_environ()
        request = Request(env)
        
        # Mock current_app to be None
        monkeypatch.setattr('flask.wrappers.current_app', None)
        
        result = request.max_form_parts
        
        # Should return the parent class implementation
        assert result == super(Request, request).max_form_parts
    
    def test_max_form_parts_with_current_app_config(self):
        """Test when current_app exists and has MAX_FORM_PARTS config."""
        app = Flask(__name__)
        app.config['MAX_FORM_PARTS'] = 2000
        
        with app.test_request_context():
            builder = EnvironBuilder()
            env = builder.get_environ()
            request = Request(env)
            
            result = request.max_form_parts
            
            assert result == 2000
    
    def test_max_form_parts_with_current_app_default_config(self):
        """Test when current_app exists but no explicit MAX_FORM_PARTS config."""
        app = Flask(__name__)
        
        with app.test_request_context():
            builder = EnvironBuilder()
            env = builder.get_environ()
            request = Request(env)
            
            result = request.max_form_parts
            
            # Should return the default value from current_app.config
            assert result == app.config['MAX_FORM_PARTS']
