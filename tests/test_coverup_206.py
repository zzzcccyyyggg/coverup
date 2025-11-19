# file: src/flask/src/flask/sansio/scaffold.py:335-365
# asked: {"lines": [335, 336, 360, 361, 362, 363, 365], "branches": []}
# gained: {"lines": [335, 336, 360, 361, 362, 363, 365], "branches": []}

import pytest
import typing as t
from unittest.mock import Mock, patch

class TestScaffoldRoute:
    """Test cases for Scaffold.route method to achieve full coverage."""
    
    def test_route_decorator_without_endpoint(self, monkeypatch):
        """Test route decorator when endpoint is not provided in options."""
        from flask.sansio.scaffold import Scaffold
        
        # Create a mock Scaffold instance with required import_name
        scaffold = Scaffold(import_name='test_app')
        
        # Mock add_url_rule to track calls
        mock_add_url_rule = Mock()
        monkeypatch.setattr(scaffold, 'add_url_rule', mock_add_url_rule)
        
        # Mock _check_setup_finished to avoid setup issues
        monkeypatch.setattr(scaffold, '_check_setup_finished', Mock())
        
        # Test the route decorator
        decorator = scaffold.route('/test')
        
        # Define a test view function
        def test_view():
            return "Hello, World!"
        
        # Apply the decorator
        decorated_view = decorator(test_view)
        
        # Verify the view function is returned unchanged
        assert decorated_view is test_view
        
        # Verify add_url_rule was called with correct arguments
        mock_add_url_rule.assert_called_once_with(
            '/test', None, test_view
        )
    
    def test_route_decorator_with_endpoint(self, monkeypatch):
        """Test route decorator when endpoint is provided in options."""
        from flask.sansio.scaffold import Scaffold
        
        # Create a mock Scaffold instance with required import_name
        scaffold = Scaffold(import_name='test_app')
        
        # Mock add_url_rule to track calls
        mock_add_url_rule = Mock()
        monkeypatch.setattr(scaffold, 'add_url_rule', mock_add_url_rule)
        
        # Mock _check_setup_finished to avoid setup issues
        monkeypatch.setattr(scaffold, '_check_setup_finished', Mock())
        
        # Test the route decorator with endpoint option
        decorator = scaffold.route('/test', endpoint='custom_endpoint')
        
        # Define a test view function
        def test_view():
            return "Hello, World!"
        
        # Apply the decorator
        decorated_view = decorator(test_view)
        
        # Verify the view function is returned unchanged
        assert decorated_view is test_view
        
        # Verify add_url_rule was called with correct arguments
        mock_add_url_rule.assert_called_once_with(
            '/test', 'custom_endpoint', test_view
        )
    
    def test_route_decorator_with_additional_options(self, monkeypatch):
        """Test route decorator with additional options like methods."""
        from flask.sansio.scaffold import Scaffold
        
        # Create a mock Scaffold instance with required import_name
        scaffold = Scaffold(import_name='test_app')
        
        # Mock add_url_rule to track calls
        mock_add_url_rule = Mock()
        monkeypatch.setattr(scaffold, 'add_url_rule', mock_add_url_rule)
        
        # Mock _check_setup_finished to avoid setup issues
        monkeypatch.setattr(scaffold, '_check_setup_finished', Mock())
        
        # Test the route decorator with additional options
        decorator = scaffold.route('/test', methods=['GET', 'POST'])
        
        # Define a test view function
        def test_view():
            return "Hello, World!"
        
        # Apply the decorator
        decorated_view = decorator(test_view)
        
        # Verify the view function is returned unchanged
        assert decorated_view is test_view
        
        # Verify add_url_rule was called with correct arguments including methods
        mock_add_url_rule.assert_called_once_with(
            '/test', None, test_view, methods=['GET', 'POST']
        )
    
    def test_route_decorator_endpoint_removed_from_options(self, monkeypatch):
        """Test that endpoint is popped from options and not passed to add_url_rule."""
        from flask.sansio.scaffold import Scaffold
        
        # Create a mock Scaffold instance with required import_name
        scaffold = Scaffold(import_name='test_app')
        
        # Mock add_url_rule to track calls
        mock_add_url_rule = Mock()
        monkeypatch.setattr(scaffold, 'add_url_rule', mock_add_url_rule)
        
        # Mock _check_setup_finished to avoid setup issues
        monkeypatch.setattr(scaffold, '_check_setup_finished', Mock())
        
        # Test the route decorator with multiple options including endpoint
        decorator = scaffold.route(
            '/test', 
            endpoint='custom_endpoint',
            methods=['GET'],
            defaults={'id': 1}
        )
        
        # Define a test view function
        def test_view():
            return "Hello, World!"
        
        # Apply the decorator
        decorated_view = decorator(test_view)
        
        # Verify the view function is returned unchanged
        assert decorated_view is test_view
        
        # Verify add_url_rule was called with endpoint popped from options
        # The endpoint should be passed as second argument, not in kwargs
        mock_add_url_rule.assert_called_once_with(
            '/test', 'custom_endpoint', test_view, methods=['GET'], defaults={'id': 1}
        )
