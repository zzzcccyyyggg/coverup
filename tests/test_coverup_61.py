# file: src/flask/src/flask/app.py:325-356
# asked: {"lines": [325, 326, 348, 349, 351, 353, 354, 356], "branches": [[348, 349], [348, 351], [353, 354], [353, 356]]}
# gained: {"lines": [325, 326, 348, 349, 351, 353, 354, 356], "branches": [[348, 349], [348, 351], [353, 354], [353, 356]]}

import pytest
import tempfile
import os
from flask import Flask

class TestFlaskOpenResource:
    """Test cases for Flask.open_resource method to achieve full coverage."""
    
    def test_open_resource_invalid_mode_raises_value_error(self):
        """Test that open_resource raises ValueError for invalid modes."""
        app = Flask(__name__)
        
        with pytest.raises(ValueError, match="Resources can only be opened for reading."):
            app.open_resource("test.txt", mode="w")
    
    def test_open_resource_binary_mode(self, tmp_path):
        """Test open_resource with binary mode."""
        app = Flask(__name__)
        app.root_path = str(tmp_path)
        
        # Create a test file
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"binary content")
        
        # Test binary mode
        with app.open_resource("test.bin", mode="rb") as f:
            content = f.read()
            assert content == b"binary content"
    
    def test_open_resource_text_mode_without_encoding(self, tmp_path):
        """Test open_resource with text mode without encoding."""
        app = Flask(__name__)
        app.root_path = str(tmp_path)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("text content")
        
        # Test text mode without encoding
        with app.open_resource("test.txt", mode="r") as f:
            content = f.read()
            assert content == "text content"
    
    def test_open_resource_text_mode_with_encoding(self, tmp_path):
        """Test open_resource with text mode with encoding."""
        app = Flask(__name__)
        app.root_path = str(tmp_path)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("text content with encoding")
        
        # Test text mode with encoding
        with app.open_resource("test.txt", mode="rt", encoding="utf-8") as f:
            content = f.read()
            assert content == "text content with encoding"
    
    def test_open_resource_rt_mode(self, tmp_path):
        """Test open_resource with 'rt' mode."""
        app = Flask(__name__)
        app.root_path = str(tmp_path)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("rt mode content")
        
        # Test 'rt' mode
        with app.open_resource("test.txt", mode="rt") as f:
            content = f.read()
            assert content == "rt mode content"
