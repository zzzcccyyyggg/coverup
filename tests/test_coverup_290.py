# file: src/flask/src/flask/app.py:874-898
# asked: {"lines": [895], "branches": [[891, 895]]}
# gained: {"lines": [895], "branches": [[891, 895]]}

import pytest
from flask import Flask
from werkzeug.routing import Rule
from flask.globals import _cv_app


class TestFlaskDispatchRequest:
    def test_dispatch_request_with_automatic_options(self):
        """Test that line 895 executes when rule has provide_automatic_options=True and method is OPTIONS"""
        app = Flask(__name__)
        
        # Create a mock request with OPTIONS method and routing_exception=None
        mock_request = type('MockRequest', (), {})()
        mock_request.routing_exception = None
        mock_request.method = 'OPTIONS'
        
        # Create a rule with provide_automatic_options=True
        mock_rule = Rule('/test')
        mock_rule.provide_automatic_options = True
        mock_rule.endpoint = 'test_endpoint'
        mock_request.url_rule = mock_rule
        mock_request.view_args = {}
        
        # Mock the app context
        class MockAppContext:
            request = mock_request
        
        mock_context = MockAppContext()
        
        # Mock make_default_options_response to verify it's called
        original_make_default_options_response = app.make_default_options_response
        def mock_make_default_options_response():
            return app.response_class()
        
        # Set the app context using the context manager approach
        token = _cv_app.set(mock_context)
        try:
            # Replace the method temporarily
            app.make_default_options_response = mock_make_default_options_response
            
            # Mock view_functions to avoid KeyError
            app.view_functions = {'test_endpoint': lambda: 'test'}
            
            # Execute dispatch_request - this should trigger line 895
            response = app.dispatch_request()
            
            # Verify that make_default_options_response was called (indirectly by checking response type)
            assert isinstance(response, type(app.response_class()))
        finally:
            # Restore the original context and method
            _cv_app.reset(token)
            app.make_default_options_response = original_make_default_options_response
