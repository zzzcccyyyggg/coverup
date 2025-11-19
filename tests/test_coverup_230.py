# file: src/flask/src/flask/sansio/app.py:823-852
# asked: {"lines": [823, 824, 851, 852], "branches": []}
# gained: {"lines": [823, 824, 851, 852], "branches": []}

import pytest
from flask import Flask

def test_teardown_appcontext_registration():
    """Test that teardown_appcontext registers functions correctly."""
    app = Flask(__name__)
    
    # Track if the teardown function was called
    teardown_called = []
    
    @app.teardown_appcontext
    def teardown_func(error):
        teardown_called.append(error)
    
    # Verify the function was registered
    assert teardown_func in app.teardown_appcontext_funcs
    
    # Test that the function is returned (line 852)
    registered_func = app.teardown_appcontext(teardown_func)
    assert registered_func is teardown_func

def test_teardown_appcontext_multiple_registrations():
    """Test that multiple teardown_appcontext functions can be registered."""
    app = Flask(__name__)
    
    teardown_calls = []
    
    @app.teardown_appcontext
    def teardown1(error):
        teardown_calls.append(('teardown1', error))
    
    @app.teardown_appcontext  
    def teardown2(error):
        teardown_calls.append(('teardown2', error))
    
    # Verify both functions were registered
    assert len(app.teardown_appcontext_funcs) == 2
    assert teardown1 in app.teardown_appcontext_funcs
    assert teardown2 in app.teardown_appcontext_funcs

def test_teardown_appcontext_with_lambda():
    """Test that lambda functions can be registered as teardown handlers."""
    app = Flask(__name__)
    
    teardown_called = []
    
    # Register a lambda function
    teardown_lambda = lambda error: teardown_called.append(error)
    registered = app.teardown_appcontext(teardown_lambda)
    
    # Verify the lambda was registered and returned
    assert teardown_lambda in app.teardown_appcontext_funcs
    assert registered is teardown_lambda

def test_teardown_appcontext_after_first_request_error():
    """Test that teardown_appcontext cannot be registered after first request."""
    app = Flask(__name__)
    
    # Simulate that setup is finished (first request has been handled)
    app._got_first_request = True
    
    # This should raise an AssertionError
    with pytest.raises(AssertionError) as exc_info:
        @app.teardown_appcontext
        def teardown_func(error):
            pass
    
    # Verify the error message mentions the setup method
    assert "The setup method 'teardown_appcontext' can no longer be called" in str(exc_info.value)
    assert "already handled its first request" in str(exc_info.value)
