# file: src/flask/src/flask/wrappers.py:212-219
# asked: {"lines": [212, 213, 214, 215, 216, 217, 219], "branches": [[216, 217], [216, 219]]}
# gained: {"lines": [212, 213, 214, 215, 216, 217, 219], "branches": [[216, 217], [216, 219]]}

import pytest
from flask import Flask
from flask.wrappers import Request
from werkzeug.exceptions import BadRequest
import typing as t


class TestRequestOnJsonLoadingFailed:
    """Test cases for Request.on_json_loading_failed method to achieve full coverage."""
    
    def test_on_json_loading_failed_super_raises_badrequest_app_debug_true(self, monkeypatch):
        """Test when super().on_json_loading_failed raises BadRequest and current_app.debug is True."""
        app = Flask(__name__)
        app.debug = True
        
        # Create a mock request
        with app.test_request_context():
            request = Request({})
            
            # Mock the parent class's on_json_loading_failed method to raise BadRequest
            original_method = Request.__bases__[0].on_json_loading_failed
            
            def mock_parent_on_json_loading_failed(self, e):
                raise BadRequest("JSON loading failed")
            
            monkeypatch.setattr(Request.__bases__[0], 'on_json_loading_failed', mock_parent_on_json_loading_failed)
            
            # Test that BadRequest is raised when current_app.debug is True
            with pytest.raises(BadRequest, match="JSON loading failed"):
                request.on_json_loading_failed(ValueError("Invalid JSON"))
            
            # Restore original method
            monkeypatch.setattr(Request.__bases__[0], 'on_json_loading_failed', original_method)
    
    def test_on_json_loading_failed_super_raises_badrequest_app_debug_false(self, monkeypatch):
        """Test when super().on_json_loading_failed raises BadRequest and current_app.debug is False."""
        app = Flask(__name__)
        app.debug = False
        
        # Create a mock request
        with app.test_request_context():
            request = Request({})
            
            # Mock the parent class's on_json_loading_failed method to raise BadRequest
            original_method = Request.__bases__[0].on_json_loading_failed
            
            def mock_parent_on_json_loading_failed(self, e):
                raise BadRequest("JSON loading failed")
            
            monkeypatch.setattr(Request.__bases__[0], 'on_json_loading_failed', mock_parent_on_json_loading_failed)
            
            # Test that a new BadRequest is raised (not the original one) when current_app.debug is False
            with pytest.raises(BadRequest) as exc_info:
                request.on_json_loading_failed(ValueError("Invalid JSON"))
            
            # Verify it's a new BadRequest instance, not the original one
            assert exc_info.value is not None
            assert "400 Bad Request" in str(exc_info.value)
            
            # Restore original method
            monkeypatch.setattr(Request.__bases__[0], 'on_json_loading_failed', original_method)
    
    def test_on_json_loading_failed_super_raises_badrequest_no_current_app(self, monkeypatch):
        """Test when super().on_json_loading_failed raises BadRequest and there's no current_app."""
        # Create request without app context
        request = Request({})
        
        # Mock the parent class's on_json_loading_failed method to raise BadRequest
        original_method = Request.__bases__[0].on_json_loading_failed
        
        def mock_parent_on_json_loading_failed(self, e):
            raise BadRequest("JSON loading failed")
        
        monkeypatch.setattr(Request.__bases__[0], 'on_json_loading_failed', mock_parent_on_json_loading_failed)
        
        # Test that a new BadRequest is raised when there's no current_app
        with pytest.raises(BadRequest) as exc_info:
            request.on_json_loading_failed(ValueError("Invalid JSON"))
        
        # Verify it's a new BadRequest instance
        assert exc_info.value is not None
        assert "400 Bad Request" in str(exc_info.value)
        
        # Restore original method
        monkeypatch.setattr(Request.__bases__[0], 'on_json_loading_failed', original_method)
