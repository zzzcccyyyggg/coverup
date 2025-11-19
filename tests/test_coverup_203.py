# file: src/flask/src/flask/wrappers.py:115-117
# asked: {"lines": [115, 116, 117], "branches": []}
# gained: {"lines": [115, 116, 117], "branches": []}

import pytest
from flask import Flask
from flask.wrappers import Request

class TestRequestMaxFormMemorySizeSetter:
    """Test cases for the max_form_memory_size setter in flask.wrappers.Request"""
    
    def test_max_form_memory_size_setter_with_int_value(self):
        """Test setting max_form_memory_size with an integer value"""
        app = Flask(__name__)
        with app.test_request_context():
            request = Request({})
            request.max_form_memory_size = 1024
            assert request._max_form_memory_size == 1024
    
    def test_max_form_memory_size_setter_with_none_value(self):
        """Test setting max_form_memory_size with None value"""
        app = Flask(__name__)
        with app.test_request_context():
            request = Request({})
            request.max_form_memory_size = None
            assert request._max_form_memory_size is None
    
    def test_max_form_memory_size_setter_with_zero_value(self):
        """Test setting max_form_memory_size with zero value"""
        app = Flask(__name__)
        with app.test_request_context():
            request = Request({})
            request.max_form_memory_size = 0
            assert request._max_form_memory_size == 0
    
    def test_max_form_memory_size_setter_with_large_int_value(self):
        """Test setting max_form_memory_size with a large integer value"""
        app = Flask(__name__)
        with app.test_request_context():
            request = Request({})
            request.max_form_memory_size = 1024 * 1024 * 100  # 100 MB
            assert request._max_form_memory_size == 1024 * 1024 * 100
