# file: src/flask/src/flask/blueprints.py:55-80
# asked: {"lines": [55, 72, 74, 75, 77, 78, 80], "branches": [[74, 75], [74, 77], [77, 78], [77, 80]]}
# gained: {"lines": [55, 72, 74, 75, 77, 78, 80], "branches": [[74, 75], [74, 77], [77, 78], [77, 80]]}

import pytest
from datetime import timedelta
from flask import Flask
from flask.blueprints import Blueprint

class TestBlueprintGetSendFileMaxAge:
    """Test cases for Blueprint.get_send_file_max_age method"""
    
    def test_get_send_file_max_age_none(self):
        """Test when SEND_FILE_MAX_AGE_DEFAULT is None"""
        app = Flask(__name__)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = None
        blueprint = Blueprint('test', __name__)
        
        with app.app_context():
            result = blueprint.get_send_file_max_age('test.txt')
            assert result is None
    
    def test_get_send_file_max_age_timedelta(self):
        """Test when SEND_FILE_MAX_AGE_DEFAULT is a timedelta"""
        app = Flask(__name__)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(hours=1)
        blueprint = Blueprint('test', __name__)
        
        with app.app_context():
            result = blueprint.get_send_file_max_age('test.txt')
            assert result == 3600
    
    def test_get_send_file_max_age_int(self):
        """Test when SEND_FILE_MAX_AGE_DEFAULT is an integer"""
        app = Flask(__name__)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
        blueprint = Blueprint('test', __name__)
        
        with app.app_context():
            result = blueprint.get_send_file_max_age('test.txt')
            assert result == 300
    
    def test_get_send_file_max_age_with_none_filename(self):
        """Test when filename is None"""
        app = Flask(__name__)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
        blueprint = Blueprint('test', __name__)
        
        with app.app_context():
            result = blueprint.get_send_file_max_age(None)
            assert result == 300
