# file: src/flask/src/flask/sansio/app.py:410-420
# asked: {"lines": [410, 411, 412, 413], "branches": [[411, 0], [411, 412]]}
# gained: {"lines": [410, 411, 412, 413], "branches": [[411, 0], [411, 412]]}

import pytest
from flask import Flask

def test_check_setup_finished_after_first_request():
    """Test that _check_setup_finished raises AssertionError after first request."""
    app = Flask(__name__)
    
    # Simulate that the app has handled its first request
    app._got_first_request = True
    
    # Try to call a setup method - this should raise AssertionError
    with pytest.raises(AssertionError) as exc_info:
        app._check_setup_finished("test_setup_method")
    
    # Verify the error message contains the expected content
    assert "The setup method 'test_setup_method' can no longer be called" in str(exc_info.value)
    assert "It has already handled its first request" in str(exc_info.value)
    assert "Make sure all imports, decorators, functions, etc." in str(exc_info.value)

def test_check_setup_finished_before_first_request():
    """Test that _check_setup_finished does nothing before first request."""
    app = Flask(__name__)
    
    # App hasn't handled first request yet
    app._got_first_request = False
    
    # This should not raise any exception
    app._check_setup_finished("test_setup_method")
