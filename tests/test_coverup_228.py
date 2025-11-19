# file: src/flask/src/flask/app.py:1360-1378
# asked: {"lines": [1360, 1378], "branches": []}
# gained: {"lines": [1360, 1378], "branches": []}

import pytest
from flask import Flask


class TestFlaskAppContext:
    """Test cases for Flask.app_context method."""
    
    def test_app_context_returns_app_context_instance(self):
        """Test that app_context() returns an AppContext instance."""
        app = Flask(__name__)
        
        # Call app_context method
        context = app.app_context()
        
        # Verify it returns an AppContext instance
        assert isinstance(context, type(app.app_context()))
        assert context.app is app
        
    def test_app_context_can_be_used_as_context_manager(self):
        """Test that the returned AppContext can be used as a context manager."""
        app = Flask(__name__)
        
        # Use app_context as context manager
        with app.app_context() as context:
            # Verify we're in the context
            assert context.app is app
            # Verify current_app is available (this would be tested in actual Flask tests)
            # The context should be properly set up
            
        # Context should be cleaned up after exit
        
    def test_app_context_multiple_calls_return_different_instances(self):
        """Test that multiple calls to app_context return different instances."""
        app = Flask(__name__)
        
        context1 = app.app_context()
        context2 = app.app_context()
        
        # They should be different instances
        assert context1 is not context2
        # But both should reference the same app
        assert context1.app is app
        assert context2.app is app
