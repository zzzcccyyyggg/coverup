# file: src/flask/src/flask/helpers.py:187-238
# asked: {"lines": [231, 232, 233, 234, 235, 236, 237], "branches": []}
# gained: {"lines": [231, 232, 233, 234, 235, 236, 237], "branches": []}

import pytest
from flask import Flask
from flask.helpers import url_for
from werkzeug.routing import BuildError


class TestUrlForCoverage:
    """Test cases to cover lines 231-237 in flask/helpers.py"""
    
    def test_url_for_calls_current_app_url_for_with_all_parameters(self):
        """Test that url_for calls current_app.url_for with all parameters including _anchor, _method, _scheme, _external, and **values"""
        app = Flask(__name__)
        
        # Mock current_app.url_for to capture the call
        captured_args = []
        captured_kwargs = {}
        
        def mock_url_for(endpoint, **kwargs):
            captured_args.append(endpoint)
            captured_kwargs.update(kwargs)
            return "http://example.com/test"
        
        # Set up the test context properly
        with app.app_context():
            # Mock the current_app.url_for method
            original_url_for = app.url_for
            app.url_for = mock_url_for
            
            try:
                # Call url_for with all parameters
                result = url_for(
                    'test_endpoint',
                    _anchor='section1',
                    _method='GET',
                    _scheme='https',
                    _external=True,
                    param1='value1',
                    param2='value2'
                )
                
                # Verify the call was made with correct parameters
                assert captured_args == ['test_endpoint']
                assert captured_kwargs == {
                    '_anchor': 'section1',
                    '_method': 'GET',
                    '_scheme': 'https',
                    '_external': True,
                    'param1': 'value1',
                    'param2': 'value2'
                }
                assert result == "http://example.com/test"
            finally:
                # Restore original method
                app.url_for = original_url_for
    
    def test_url_for_calls_current_app_url_for_with_minimal_parameters(self):
        """Test that url_for calls current_app.url_for with minimal parameters (only endpoint)"""
        app = Flask(__name__)
        
        # Mock current_app.url_for to capture the call
        captured_args = []
        captured_kwargs = {}
        
        def mock_url_for(endpoint, **kwargs):
            captured_args.append(endpoint)
            captured_kwargs.update(kwargs)
            return "/test"
        
        # Set up the test context properly
        with app.app_context():
            # Mock the current_app.url_for method
            original_url_for = app.url_for
            app.url_for = mock_url_for
            
            try:
                # Call url_for with only endpoint
                result = url_for('minimal_endpoint')
                
                # Verify the call was made with correct parameters
                assert captured_args == ['minimal_endpoint']
                assert captured_kwargs == {
                    '_anchor': None,
                    '_method': None,
                    '_scheme': None,
                    '_external': None
                }
                assert result == "/test"
            finally:
                # Restore original method
                app.url_for = original_url_for
    
    def test_url_for_calls_current_app_url_for_with_partial_parameters(self):
        """Test that url_for calls current_app.url_for with some optional parameters"""
        app = Flask(__name__)
        
        # Mock current_app.url_for to capture the call
        captured_args = []
        captured_kwargs = {}
        
        def mock_url_for(endpoint, **kwargs):
            captured_args.append(endpoint)
            captured_kwargs.update(kwargs)
            return "/test#section"
        
        # Set up the test context properly
        with app.app_context():
            # Mock the current_app.url_for method
            original_url_for = app.url_for
            app.url_for = mock_url_for
            
            try:
                # Call url_for with some optional parameters
                result = url_for(
                    'partial_endpoint',
                    _anchor='section',
                    param='value'
                )
                
                # Verify the call was made with correct parameters
                assert captured_args == ['partial_endpoint']
                assert captured_kwargs == {
                    '_anchor': 'section',
                    '_method': None,
                    '_scheme': None,
                    '_external': None,
                    'param': 'value'
                }
                assert result == "/test#section"
            finally:
                # Restore original method
                app.url_for = original_url_for
    
    def test_url_for_calls_current_app_url_for_with_external_scheme(self):
        """Test that url_for calls current_app.url_for with _scheme and _external parameters"""
        app = Flask(__name__)
        
        # Mock current_app.url_for to capture the call
        captured_args = []
        captured_kwargs = {}
        
        def mock_url_for(endpoint, **kwargs):
            captured_args.append(endpoint)
            captured_kwargs.update(kwargs)
            return "https://example.com/test"
        
        # Set up the test context properly
        with app.app_context():
            # Mock the current_app.url_for method
            original_url_for = app.url_for
            app.url_for = mock_url_for
            
            try:
                # Call url_for with scheme parameters
                result = url_for(
                    'external_endpoint',
                    _scheme='https',
                    _external=True
                )
                
                # Verify the call was made with correct parameters
                assert captured_args == ['external_endpoint']
                assert captured_kwargs == {
                    '_anchor': None,
                    '_method': None,
                    '_scheme': 'https',
                    '_external': True
                }
                assert result == "https://example.com/test"
            finally:
                # Restore original method
                app.url_for = original_url_for
    
    def test_url_for_calls_current_app_url_for_with_method_only(self):
        """Test that url_for calls current_app.url_for with only _method parameter"""
        app = Flask(__name__)
        
        # Mock current_app.url_for to capture the call
        captured_args = []
        captured_kwargs = {}
        
        def mock_url_for(endpoint, **kwargs):
            captured_args.append(endpoint)
            captured_kwargs.update(kwargs)
            return "/test"
        
        # Set up the test context properly
        with app.app_context():
            # Mock the current_app.url_for method
            original_url_for = app.url_for
            app.url_for = mock_url_for
            
            try:
                # Call url_for with method only
                result = url_for(
                    'method_endpoint',
                    _method='POST'
                )
                
                # Verify the call was made with correct parameters
                assert captured_args == ['method_endpoint']
                assert captured_kwargs == {
                    '_anchor': None,
                    '_method': 'POST',
                    '_scheme': None,
                    '_external': None
                }
                assert result == "/test"
            finally:
                # Restore original method
                app.url_for = original_url_for
