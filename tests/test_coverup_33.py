# file: src/flask/src/flask/sansio/app.py:890-923
# asked: {"lines": [890, 907, 908, 910, 913, 914, 915, 916, 918, 920, 921, 923], "branches": [[907, 908], [907, 910], [913, 918], [913, 920], [920, 921], [920, 923]]}
# gained: {"lines": [890, 907, 908, 910, 913, 914, 915, 916, 918, 920, 921, 923], "branches": [[907, 908], [907, 910], [913, 918], [913, 920], [920, 921], [920, 923]]}

import pytest
from werkzeug.exceptions import BadRequest, BadRequestKeyError
from flask import Flask

class TestTrapHttpException:
    """Test cases for App.trap_http_exception method to achieve full coverage."""
    
    def test_trap_http_exceptions_true(self):
        """Test when TRAP_HTTP_EXCEPTIONS is True - should return True for any exception."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = True
        
        # Test with BadRequest
        result1 = app.trap_http_exception(BadRequest())
        assert result1 is True
        
        # Test with BadRequestKeyError
        result2 = app.trap_http_exception(BadRequestKeyError("test"))
        assert result2 is True
        
        # Test with generic Exception
        result3 = app.trap_http_exception(Exception("generic"))
        assert result3 is True

    def test_trap_bad_request_errors_none_debug_true_bad_request_key_error(self):
        """Test when TRAP_BAD_REQUEST_ERRORS is None, debug is True, and exception is BadRequestKeyError."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = False
        app.config["TRAP_BAD_REQUEST_ERRORS"] = None
        app.debug = True
        
        result = app.trap_http_exception(BadRequestKeyError("test"))
        assert result is True

    def test_trap_bad_request_errors_none_debug_true_other_exception(self):
        """Test when TRAP_BAD_REQUEST_ERRORS is None, debug is True, but exception is not BadRequestKeyError."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = False
        app.config["TRAP_BAD_REQUEST_ERRORS"] = None
        app.debug = True
        
        result = app.trap_http_exception(BadRequest())
        assert result is False

    def test_trap_bad_request_errors_none_debug_false_bad_request_key_error(self):
        """Test when TRAP_BAD_REQUEST_ERRORS is None, debug is False, and exception is BadRequestKeyError."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = False
        app.config["TRAP_BAD_REQUEST_ERRORS"] = None
        app.debug = False
        
        result = app.trap_http_exception(BadRequestKeyError("test"))
        assert result is False

    def test_trap_bad_request_errors_true_bad_request(self):
        """Test when TRAP_BAD_REQUEST_ERRORS is True and exception is BadRequest."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = False
        app.config["TRAP_BAD_REQUEST_ERRORS"] = True
        
        result = app.trap_http_exception(BadRequest())
        assert result is True

    def test_trap_bad_request_errors_true_bad_request_key_error(self):
        """Test when TRAP_BAD_REQUEST_ERRORS is True and exception is BadRequestKeyError."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = False
        app.config["TRAP_BAD_REQUEST_ERRORS"] = True
        
        result = app.trap_http_exception(BadRequestKeyError("test"))
        assert result is True

    def test_trap_bad_request_errors_true_other_exception(self):
        """Test when TRAP_BAD_REQUEST_ERRORS is True but exception is not BadRequest."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = False
        app.config["TRAP_BAD_REQUEST_ERRORS"] = True
        
        result = app.trap_http_exception(Exception("generic"))
        assert result is False

    def test_trap_bad_request_errors_false(self):
        """Test when TRAP_BAD_REQUEST_ERRORS is False - should return False."""
        app = Flask(__name__)
        app.config["TRAP_HTTP_EXCEPTIONS"] = False
        app.config["TRAP_BAD_REQUEST_ERRORS"] = False
        
        # Test with BadRequest
        result1 = app.trap_http_exception(BadRequest())
        assert result1 is False
        
        # Test with BadRequestKeyError
        result2 = app.trap_http_exception(BadRequestKeyError("test"))
        assert result2 is False
        
        # Test with generic Exception
        result3 = app.trap_http_exception(Exception("generic"))
        assert result3 is False
