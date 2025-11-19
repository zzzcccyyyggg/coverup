# file: src/flask/src/flask/app.py:276-301
# asked: {"lines": [276, 293, 295, 296, 298, 299, 301], "branches": [[295, 296], [295, 298], [298, 299], [298, 301]]}
# gained: {"lines": [276, 293, 295, 296, 298, 299, 301], "branches": [[295, 296], [295, 298], [298, 299], [298, 301]]}

import pytest
from datetime import timedelta
from flask import Flask

class TestGetSendFileMaxAge:
    """Test cases for Flask.get_send_file_max_age method."""
    
    def test_get_send_file_max_age_none_config(self):
        """Test when SEND_FILE_MAX_AGE_DEFAULT is None."""
        app = Flask(__name__)
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = None
        result = app.get_send_file_max_age("test.txt")
        assert result is None

    def test_get_send_file_max_age_timedelta_config(self):
        """Test when SEND_FILE_MAX_AGE_DEFAULT is a timedelta."""
        app = Flask(__name__)
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = timedelta(hours=2)
        result = app.get_send_file_max_age("test.txt")
        assert result == 7200  # 2 hours in seconds

    def test_get_send_file_max_age_int_config(self):
        """Test when SEND_FILE_MAX_AGE_DEFAULT is an integer."""
        app = Flask(__name__)
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600
        result = app.get_send_file_max_age("test.txt")
        assert result == 3600

    def test_get_send_file_max_age_with_none_filename(self):
        """Test with None filename parameter."""
        app = Flask(__name__)
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1800
        result = app.get_send_file_max_age(None)
        assert result == 1800

    def test_get_send_file_max_age_with_empty_filename(self):
        """Test with empty string filename parameter."""
        app = Flask(__name__)
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = timedelta(minutes=30)
        result = app.get_send_file_max_age("")
        assert result == 1800  # 30 minutes in seconds
