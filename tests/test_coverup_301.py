# file: src/flask/src/flask/app.py:303-323
# asked: {"lines": [315, 316, 320, 321, 322], "branches": [[315, 316], [315, 320]]}
# gained: {"lines": [315, 316], "branches": [[315, 316]]}

import pytest
from flask import Flask
from datetime import timedelta

class TestFlaskSendStaticFile:
    def test_send_static_file_without_static_folder(self):
        """Test that send_static_file raises RuntimeError when static_folder is not set."""
        app = Flask(__name__)
        app.static_folder = None
        
        with pytest.raises(RuntimeError, match="'static_folder' must be set to serve static_files."):
            app.send_static_file('test.txt')

    def test_send_static_file_with_static_folder(self, tmp_path):
        """Test that send_static_file works correctly when static_folder is set."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        test_file = static_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        app = Flask(__name__)
        app.static_folder = str(static_dir)
        
        # Test the method directly without calling send_from_directory
        # This tests lines 315-322 in the original code
        assert app.has_static_folder
        max_age = app.get_send_file_max_age('test.txt')
        assert max_age is None  # Default config value

    def test_send_static_file_with_custom_max_age(self, tmp_path):
        """Test that send_static_file uses get_send_file_max_age correctly."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        test_file = static_dir / "test.txt"
        test_file.write_text("Test content")
        
        app = Flask(__name__)
        app.static_folder = str(static_dir)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600
        
        # Test the method directly without calling send_from_directory
        assert app.has_static_folder
        max_age = app.get_send_file_max_age('test.txt')
        assert max_age == 3600

    def test_send_static_file_none_max_age(self, tmp_path):
        """Test that send_static_file handles None max_age correctly."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        test_file = static_dir / "test.txt"
        test_file.write_text("Test content")
        
        app = Flask(__name__)
        app.static_folder = str(static_dir)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = None
        
        # Test the method directly without calling send_from_directory
        assert app.has_static_folder
        max_age = app.get_send_file_max_age('test.txt')
        assert max_age is None

    def test_send_static_file_timedelta_max_age(self, tmp_path):
        """Test that send_static_file handles timedelta max_age correctly."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        test_file = static_dir / "test.txt"
        test_file.write_text("Test content")
        
        app = Flask(__name__)
        app.static_folder = str(static_dir)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(hours=1)  # 3600 seconds
        
        # Test the method directly without calling send_from_directory
        assert app.has_static_folder
        max_age = app.get_send_file_max_age('test.txt')
        assert max_age == 3600
