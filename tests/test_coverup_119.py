# file: src/flask/src/flask/app.py:358-378
# asked: {"lines": [358, 359, 373, 375, 376, 378], "branches": [[375, 376], [375, 378]]}
# gained: {"lines": [358, 359, 373, 375, 376, 378], "branches": [[375, 376], [375, 378]]}

import os
import tempfile
import pytest
from flask import Flask

class TestFlaskOpenInstanceResource:
    def test_open_instance_resource_binary_mode(self, tmp_path):
        """Test opening instance resource in binary mode."""
        app = Flask(__name__, instance_path=str(tmp_path))
        
        # Create a test file in the instance folder
        test_file = tmp_path / "test_binary.dat"
        test_file.write_bytes(b"binary data")
        
        # Test binary mode
        with app.open_instance_resource("test_binary.dat", "rb") as f:
            content = f.read()
            assert content == b"binary data"
    
    def test_open_instance_resource_text_mode_default_encoding(self, tmp_path):
        """Test opening instance resource in text mode with default encoding."""
        app = Flask(__name__, instance_path=str(tmp_path))
        
        # Create a test file in the instance folder
        test_file = tmp_path / "test_text.txt"
        test_file.write_text("text data", encoding="utf-8")
        
        # Test text mode with default encoding (utf-8)
        with app.open_instance_resource("test_text.txt", "r") as f:
            content = f.read()
            assert content == "text data"
    
    def test_open_instance_resource_text_mode_custom_encoding(self, tmp_path):
        """Test opening instance resource in text mode with custom encoding."""
        app = Flask(__name__, instance_path=str(tmp_path))
        
        # Create a test file in the instance folder with latin-1 encoding
        test_file = tmp_path / "test_latin1.txt"
        test_file.write_bytes("café".encode("latin-1"))
        
        # Test text mode with latin-1 encoding
        with app.open_instance_resource("test_latin1.txt", "r", encoding="latin-1") as f:
            content = f.read()
            assert content == "café"
    
    def test_open_instance_resource_write_mode(self, tmp_path):
        """Test opening instance resource for writing."""
        app = Flask(__name__, instance_path=str(tmp_path))
        
        # Test writing in text mode
        with app.open_instance_resource("new_file.txt", "w") as f:
            f.write("new content")
        
        # Verify the file was created and contains the content
        test_file = tmp_path / "new_file.txt"
        assert test_file.exists()
        assert test_file.read_text() == "new content"
    
    def test_open_instance_resource_write_binary_mode(self, tmp_path):
        """Test opening instance resource for writing in binary mode."""
        app = Flask(__name__, instance_path=str(tmp_path))
        
        # Test writing in binary mode
        with app.open_instance_resource("new_binary.dat", "wb") as f:
            f.write(b"binary content")
        
        # Verify the file was created and contains the content
        test_file = tmp_path / "new_binary.dat"
        assert test_file.exists()
        assert test_file.read_bytes() == b"binary content"
    
    def test_open_instance_resource_nested_path(self, tmp_path):
        """Test opening instance resource with nested path."""
        app = Flask(__name__, instance_path=str(tmp_path))
        
        # Create nested directory
        nested_dir = tmp_path / "subdir"
        nested_dir.mkdir()
        
        # Create test file in nested directory
        test_file = nested_dir / "nested.txt"
        test_file.write_text("nested content", encoding="utf-8")
        
        # Test opening file with nested path
        with app.open_instance_resource("subdir/nested.txt", "r") as f:
            content = f.read()
            assert content == "nested content"
