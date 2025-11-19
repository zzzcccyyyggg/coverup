# file: src/flask/src/flask/app.py:1343-1358
# asked: {"lines": [1343, 1355, 1356, 1358], "branches": [[1355, 1356], [1355, 1358]]}
# gained: {"lines": [1343, 1355, 1356, 1358], "branches": [[1355, 1356], [1355, 1358]]}

import pytest
from flask import Flask
from flask.signals import appcontext_tearing_down

class TestFlaskDoTeardownAppcontext:
    """Test cases for Flask.do_teardown_appcontext method."""
    
    def test_do_teardown_appcontext_with_no_teardown_funcs(self):
        """Test do_teardown_appcontext when no teardown functions are registered."""
        app = Flask(__name__)
        
        # Mock the signal to verify it's called
        signal_called = False
        def mock_signal_send(sender, _async_wrapper=None, exc=None):
            nonlocal signal_called
            signal_called = True
            assert sender is app
            assert exc is None
        
        # Patch the signal send method
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(appcontext_tearing_down, 'send', mock_signal_send)
            
            # Call the method
            app.do_teardown_appcontext()
            
            # Verify signal was called
            assert signal_called is True
    
    def test_do_teardown_appcontext_with_teardown_funcs(self):
        """Test do_teardown_appcontext with registered teardown functions."""
        app = Flask(__name__)
        
        # Track calls to teardown functions
        teardown_calls = []
        
        def teardown_func1(exc):
            teardown_calls.append(('func1', exc))
        
        def teardown_func2(exc):
            teardown_calls.append(('func2', exc))
        
        # Register teardown functions
        app.teardown_appcontext(teardown_func1)
        app.teardown_appcontext(teardown_func2)
        
        # Mock the signal to verify it's called
        signal_called = False
        def mock_signal_send(sender, _async_wrapper=None, exc=None):
            nonlocal signal_called
            signal_called = True
            assert sender is app
            assert exc is None
        
        # Patch the signal send method
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(appcontext_tearing_down, 'send', mock_signal_send)
            
            # Call the method
            app.do_teardown_appcontext()
            
            # Verify teardown functions were called in reverse order
            assert teardown_calls == [('func2', None), ('func1', None)]
            
            # Verify signal was called
            assert signal_called is True
    
    def test_do_teardown_appcontext_with_exception(self):
        """Test do_teardown_appcontext with an exception parameter."""
        app = Flask(__name__)
        
        # Track calls to teardown functions
        teardown_calls = []
        
        def teardown_func(exc):
            teardown_calls.append(('func', exc))
        
        # Register teardown function
        app.teardown_appcontext(teardown_func)
        
        # Create a test exception
        test_exc = ValueError("Test error")
        
        # Mock the signal to verify it's called with the exception
        signal_called = False
        def mock_signal_send(sender, _async_wrapper=None, exc=None):
            nonlocal signal_called
            signal_called = True
            assert sender is app
            assert exc is test_exc
        
        # Patch the signal send method
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(appcontext_tearing_down, 'send', mock_signal_send)
            
            # Call the method with exception
            app.do_teardown_appcontext(test_exc)
            
            # Verify teardown function was called with exception
            assert teardown_calls == [('func', test_exc)]
            
            # Verify signal was called with exception
            assert signal_called is True
    
    def test_do_teardown_appcontext_with_async_wrapper(self):
        """Test do_teardown_appcontext verifies _async_wrapper parameter is passed to signal."""
        app = Flask(__name__)
        
        # Track signal parameters
        signal_params = {}
        
        def mock_signal_send(sender, _async_wrapper=None, exc=None):
            signal_params['sender'] = sender
            signal_params['_async_wrapper'] = _async_wrapper
            signal_params['exc'] = exc
        
        # Patch the signal send method
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(appcontext_tearing_down, 'send', mock_signal_send)
            
            # Call the method
            app.do_teardown_appcontext()
            
            # Verify _async_wrapper parameter is callable (not testing identity)
            assert signal_params['sender'] is app
            assert callable(signal_params['_async_wrapper'])
            assert signal_params['exc'] is None
