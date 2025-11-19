# file: src/flask/src/flask/helpers.py:527-568
# asked: {"lines": [527, 566, 567], "branches": []}
# gained: {"lines": [527, 566, 567], "branches": []}

import os
import tempfile
import pytest
from flask import Flask
from flask.helpers import send_from_directory
from werkzeug.exceptions import NotFound


class TestSendFromDirectory:
    """Test cases for send_from_directory function to achieve full coverage."""
    
    def test_send_from_directory_basic(self, tmp_path):
        """Test basic send_from_directory functionality."""
        app = Flask(__name__)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        with app.test_request_context():
            response = send_from_directory(str(tmp_path), "test.txt")
            assert response.status_code == 200
            # Don't try to read response data as it's in direct passthrough mode
    
    def test_send_from_directory_with_kwargs(self, tmp_path):
        """Test send_from_directory with additional kwargs."""
        app = Flask(__name__)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        with app.test_request_context():
            response = send_from_directory(
                str(tmp_path), 
                "test.txt", 
                as_attachment=True,
                download_name="custom.txt"
            )
            assert response.status_code == 200
            assert "attachment" in response.headers.get("Content-Disposition", "")
    
    def test_send_from_directory_with_max_age(self, tmp_path):
        """Test send_from_directory with max_age parameter."""
        app = Flask(__name__)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        with app.test_request_context():
            # Test with explicit max_age
            response = send_from_directory(
                str(tmp_path), 
                "test.txt", 
                max_age=3600
            )
            assert response.status_code == 200
            
            # Test without max_age (should use app default)
            app.get_send_file_max_age = lambda filename: 1800
            response = send_from_directory(str(tmp_path), "test.txt")
            assert response.status_code == 200
    
    def test_send_from_directory_file_not_found(self, tmp_path):
        """Test send_from_directory with non-existent file."""
        app = Flask(__name__)
        
        with app.test_request_context():
            with pytest.raises(NotFound):
                send_from_directory(str(tmp_path), "nonexistent.txt")
    
    def test_send_from_directory_with_root_path(self, tmp_path):
        """Test send_from_directory with _root_path in kwargs."""
        app = Flask(__name__)
        
        # Create a subdirectory and file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.txt"
        test_file.write_text("Hello, World!")
        
        with app.test_request_context():
            # This should trigger the _root_path handling in werkzeug
            response = send_from_directory(
                str(subdir), 
                "test.txt", 
                _root_path=str(tmp_path)
            )
            assert response.status_code == 200
    
    def test_send_from_directory_path_traversal_prevention(self, tmp_path):
        """Test that path traversal attempts are prevented."""
        app = Flask(__name__)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        with app.test_request_context():
            # Attempt path traversal - should raise NotFound
            with pytest.raises(NotFound):
                send_from_directory(str(tmp_path), "../test.txt")
            
            # Another path traversal attempt
            with pytest.raises(NotFound):
                send_from_directory(str(tmp_path), "../../etc/passwd")
    
    def test_send_from_directory_with_use_x_sendfile(self, tmp_path):
        """Test send_from_directory with USE_X_SENDFILE configuration."""
        app = Flask(__name__)
        app.config['USE_X_SENDFILE'] = True
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        with app.test_request_context():
            response = send_from_directory(str(tmp_path), "test.txt")
            assert response.status_code == 200
    
    def test_send_from_directory_with_different_response_class(self, tmp_path):
        """Test send_from_directory with custom response class."""
        app = Flask(__name__)
        
        # Create a custom response class
        from flask import Response
        
        class CustomResponse(Response):
            pass
        
        app.response_class = CustomResponse
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        with app.test_request_context():
            response = send_from_directory(str(tmp_path), "test.txt")
            assert response.status_code == 200
            assert isinstance(response, CustomResponse)
