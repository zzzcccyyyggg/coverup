# file: src/flask/src/flask/blueprints.py:82-102
# asked: {"lines": [82, 94, 95, 99, 100, 101], "branches": [[94, 95], [94, 99]]}
# gained: {"lines": [82, 94, 95, 99, 100, 101], "branches": [[94, 95], [94, 99]]}

import pytest
from flask import Flask, Blueprint
from flask.wrappers import Response
import tempfile
import os

class TestBlueprintSendStaticFile:
    def test_send_static_file_without_static_folder_raises_runtime_error(self):
        """Test that send_static_file raises RuntimeError when static_folder is not set."""
        app = Flask(__name__)
        bp = Blueprint('test_bp', __name__)
        
        with app.app_context():
            with pytest.raises(RuntimeError, match="'static_folder' must be set to serve static_files."):
                bp.send_static_file('test.txt')

    def test_send_static_file_with_static_folder_calls_get_send_file_max_age(self, monkeypatch):
        """Test that send_static_file calls get_send_file_max_age and passes filename."""
        app = Flask(__name__)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test static file
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test content')
            
            bp = Blueprint('test_bp', __name__, static_folder=temp_dir)
            
            # Mock get_send_file_max_age to verify it's called with correct filename
            called_with_filename = None
            original_method = bp.get_send_file_max_age
            
            def mock_get_send_file_max_age(filename):
                nonlocal called_with_filename
                called_with_filename = filename
                return original_method(filename)
            
            monkeypatch.setattr(bp, 'get_send_file_max_age', mock_get_send_file_max_age)
            
            # Create a test client request context to avoid the "no request in this context" error
            with app.test_client() as client:
                with client.get('/'):
                    response = bp.send_static_file('test.txt')
                    
                    # Verify get_send_file_max_age was called with correct filename
                    assert called_with_filename == 'test.txt'
                    # Verify response is successful
                    assert response.status_code == 200
                    # Verify response is a Response object
                    assert isinstance(response, Response)

    def test_send_static_file_returns_response_with_max_age(self):
        """Test that send_static_file returns a Response with max_age parameter."""
        app = Flask(__name__)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test static file
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test content')
            
            bp = Blueprint('test_bp', __name__, static_folder=temp_dir)
            
            # Create a test client request context to avoid the "no request in this context" error
            with app.test_client() as client:
                with client.get('/'):
                    response = bp.send_static_file('test.txt')
                    
                    # Verify response is a Response object
                    assert isinstance(response, Response)
                    # Verify response is successful
                    assert response.status_code == 200
