# file: src/flask/src/flask/sansio/app.py:974-1006
# asked: {"lines": [974, 991, 992, 993, 994, 996, 998, 999, 1003, 1004, 1006], "branches": [[991, 992], [991, 1003], [998, 991], [998, 999], [1003, 1004], [1003, 1006]]}
# gained: {"lines": [974, 991, 992, 993, 994, 996, 998, 999, 1003, 1004, 1006], "branches": [[991, 992], [991, 1003], [998, 991], [998, 999], [1003, 1004], [1003, 1006]]}

import pytest
from werkzeug.routing import BuildError
from flask import Flask

def test_handle_url_build_error_no_handlers():
    """Test handle_url_build_error when no handlers are registered."""
    app = Flask(__name__)
    error = BuildError("test", "test_endpoint", {})
    
    with pytest.raises(BuildError):
        app.handle_url_build_error(error, "test_endpoint", {})

def test_handle_url_build_error_handler_returns_none():
    """Test handle_url_build_error when handler returns None."""
    app = Flask(__name__)
    
    def handler_returns_none(error, endpoint, values):
        return None
    
    app.url_build_error_handlers.append(handler_returns_none)
    error = BuildError("test", "test_endpoint", {})
    
    with pytest.raises(BuildError):
        app.handle_url_build_error(error, "test_endpoint", {})

def test_handle_url_build_error_handler_raises_build_error():
    """Test handle_url_build_error when handler raises BuildError."""
    app = Flask(__name__)
    
    def handler_raises_error(error, endpoint, values):
        raise BuildError("new error", endpoint, values)
    
    app.url_build_error_handlers.append(handler_raises_error)
    original_error = BuildError("original", "test_endpoint", {})
    
    with pytest.raises(BuildError) as exc_info:
        app.handle_url_build_error(original_error, "test_endpoint", {})
    
    # Check that the error endpoint is the one from the handler
    assert exc_info.value.endpoint == "new error"

def test_handle_url_build_error_handler_returns_value():
    """Test handle_url_build_error when handler returns a value."""
    app = Flask(__name__)
    
    def handler_returns_value(error, endpoint, values):
        return "custom_url"
    
    app.url_build_error_handlers.append(handler_returns_value)
    error = BuildError("test", "test_endpoint", {})
    
    result = app.handle_url_build_error(error, "test_endpoint", {})
    assert result == "custom_url"

def test_handle_url_build_error_multiple_handlers_first_returns():
    """Test handle_url_build_error with multiple handlers, first returns value."""
    app = Flask(__name__)
    
    def first_handler_returns(error, endpoint, values):
        return "first_url"
    
    def second_handler_returns(error, endpoint, values):
        return "second_url"
    
    app.url_build_error_handlers.extend([first_handler_returns, second_handler_returns])
    error = BuildError("test", "test_endpoint", {})
    
    result = app.handle_url_build_error(error, "test_endpoint", {})
    assert result == "first_url"

def test_handle_url_build_error_multiple_handlers_first_none_second_returns():
    """Test handle_url_build_error with multiple handlers, first returns None, second returns value."""
    app = Flask(__name__)
    
    def first_handler_none(error, endpoint, values):
        return None
    
    def second_handler_returns(error, endpoint, values):
        return "second_url"
    
    app.url_build_error_handlers.extend([first_handler_none, second_handler_returns])
    error = BuildError("test", "test_endpoint", {})
    
    result = app.handle_url_build_error(error, "test_endpoint", {})
    assert result == "second_url"

def test_handle_url_build_error_multiple_handlers_first_raises_second_returns():
    """Test handle_url_build_error with multiple handlers, first raises BuildError, second returns value."""
    app = Flask(__name__)
    
    def first_handler_raises(error, endpoint, values):
        raise BuildError("first error", endpoint, values)
    
    def second_handler_returns(error, endpoint, values):
        return "second_url"
    
    app.url_build_error_handlers.extend([first_handler_raises, second_handler_returns])
    original_error = BuildError("original", "test_endpoint", {})
    
    result = app.handle_url_build_error(original_error, "test_endpoint", {})
    assert result == "second_url"

def test_handle_url_build_error_multiple_handlers_all_raise():
    """Test handle_url_build_error with multiple handlers, all raise BuildError."""
    app = Flask(__name__)
    
    def first_handler_raises(error, endpoint, values):
        raise BuildError("first error", endpoint, values)
    
    def second_handler_raises(error, endpoint, values):
        raise BuildError("second error", endpoint, values)
    
    app.url_build_error_handlers.extend([first_handler_raises, second_handler_raises])
    original_error = BuildError("original", "test_endpoint", {})
    
    with pytest.raises(BuildError) as exc_info:
        app.handle_url_build_error(original_error, "test_endpoint", {})
    
    # Check that the error endpoint is the one from the last handler
    assert exc_info.value.endpoint == "second error"

def test_handle_url_build_error_with_active_exception():
    """Test handle_url_build_error when called with an active exception."""
    app = Flask(__name__)
    
    def handler_returns_none(error, endpoint, values):
        return None
    
    app.url_build_error_handlers.append(handler_returns_none)
    error = BuildError("test", "test_endpoint", {})
    
    # Simulate being called with an active exception
    try:
        raise error
    except BuildError:
        with pytest.raises(BuildError) as exc_info:
            app.handle_url_build_error(error, "test_endpoint", {})
        
        assert exc_info.value is error
