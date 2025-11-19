# file: src/flask/src/flask/sansio/blueprints.py:655-670
# asked: {"lines": [663, 664, 665, 667, 668, 670], "branches": []}
# gained: {"lines": [663, 664, 665, 667, 668, 670], "branches": []}

import pytest
from flask.sansio.blueprints import Blueprint
from flask.sansio.blueprints import BlueprintSetupState

class TestBlueprintAppErrorHandler:
    def test_app_errorhandler_registers_error_handler_on_app(self, monkeypatch):
        """Test that app_errorhandler decorator registers error handler on the app."""
        bp = Blueprint('test_bp', __name__)
        
        # Create a mock error handler function
        def error_handler(error):
            return f"Error handled: {error}", 500
        
        # Apply the decorator
        decorated_handler = bp.app_errorhandler(500)(error_handler)
        
        # Verify the function was returned unchanged
        assert decorated_handler is error_handler
        
        # Create a mock app for BlueprintSetupState
        class MockApp:
            def __init__(self):
                self.errorhandler_calls = []
            
            def errorhandler(self, code):
                self.errorhandler_calls.append(code)
                return lambda f: f
        
        mock_app = MockApp()
        
        # Create a BlueprintSetupState to simulate blueprint registration
        state = BlueprintSetupState(bp, mock_app, {}, True)
        
        # Execute the deferred function that should have been recorded
        assert len(bp.deferred_functions) == 1
        deferred_func = bp.deferred_functions[0]
        
        # Execute the deferred function
        deferred_func(state)
        
        # Verify app.errorhandler was called with the correct code
        assert mock_app.errorhandler_calls == [500]

    def test_app_errorhandler_with_exception_class(self, monkeypatch):
        """Test that app_errorhandler works with exception classes."""
        bp = Blueprint('test_bp', __name__)
        
        class CustomException(Exception):
            pass
        
        # Create a mock error handler function
        def error_handler(error):
            return f"Custom exception handled: {error}", 500
        
        # Apply the decorator with exception class
        decorated_handler = bp.app_errorhandler(CustomException)(error_handler)
        
        # Verify the function was returned unchanged
        assert decorated_handler is error_handler
        
        # Create a mock app for BlueprintSetupState
        class MockApp:
            def __init__(self):
                self.errorhandler_calls = []
            
            def errorhandler(self, exception_class):
                self.errorhandler_calls.append(exception_class)
                return lambda f: f
        
        mock_app = MockApp()
        
        # Create a BlueprintSetupState to simulate blueprint registration
        state = BlueprintSetupState(bp, mock_app, {}, True)
        
        # Execute the deferred function that should have been recorded
        assert len(bp.deferred_functions) == 1
        deferred_func = bp.deferred_functions[0]
        
        # Execute the deferred function
        deferred_func(state)
        
        # Verify app.errorhandler was called with the correct exception class
        assert mock_app.errorhandler_calls == [CustomException]
