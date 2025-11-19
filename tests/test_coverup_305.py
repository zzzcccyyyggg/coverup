# file: src/flask/src/flask/sansio/blueprints.py:589-611
# asked: {"lines": [609], "branches": []}
# gained: {"lines": [609], "branches": []}

import pytest
from flask import Flask
from flask.sansio.blueprints import Blueprint

def test_add_app_template_global_with_name():
    """Test that add_app_template_global registers a template global with a custom name."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    def template_func():
        return "test_value"
    
    # Register the template global with a custom name
    bp.add_app_template_global(template_func, name='custom_global')
    
    # Create a setup state and call the deferred function
    state = bp.make_setup_state(app, {}, first_registration=True)
    
    # Mock the app's add_template_global method to verify it's called
    called_with = []
    original_add_template_global = app.add_template_global
    
    def mock_add_template_global(func, name=None):
        called_with.append((func, name))
    
    app.add_template_global = mock_add_template_global
    
    try:
        # Execute the deferred functions
        for deferred_func in bp.deferred_functions:
            deferred_func(state)
        
        # Verify the template global was registered with the correct name
        assert len(called_with) == 1
        assert called_with[0][0] == template_func
        assert called_with[0][1] == 'custom_global'
    finally:
        # Restore original method
        app.add_template_global = original_add_template_global

def test_add_app_template_global_without_name():
    """Test that add_app_template_global registers a template global without a name (uses function name)."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    def template_func():
        return "test_value"
    
    # Register the template global without a name
    bp.add_app_template_global(template_func)
    
    # Create a setup state and call the deferred function
    state = bp.make_setup_state(app, {}, first_registration=True)
    
    # Mock the app's add_template_global method to verify it's called
    called_with = []
    original_add_template_global = app.add_template_global
    
    def mock_add_template_global(func, name=None):
        called_with.append((func, name))
    
    app.add_template_global = mock_add_template_global
    
    try:
        # Execute the deferred functions
        for deferred_func in bp.deferred_functions:
            deferred_func(state)
        
        # Verify the template global was registered without a name
        assert len(called_with) == 1
        assert called_with[0][0] == template_func
        assert called_with[0][1] is None
    finally:
        # Restore original method
        app.add_template_global = original_add_template_global

def test_add_app_template_global_only_called_once():
    """Test that the template global registration is only called on first registration."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    def template_func():
        return "test_value"
    
    # Register the template global
    bp.add_app_template_global(template_func, name='test_global')
    
    # Create setup states for first and subsequent registrations
    state_first = bp.make_setup_state(app, {}, first_registration=True)
    state_subsequent = bp.make_setup_state(app, {}, first_registration=False)
    
    # Mock the app's add_template_global method to track calls
    call_count = 0
    original_add_template_global = app.add_template_global
    
    def mock_add_template_global(func, name=None):
        nonlocal call_count
        call_count += 1
    
    app.add_template_global = mock_add_template_global
    
    try:
        # Execute deferred functions on first registration
        for deferred_func in bp.deferred_functions:
            deferred_func(state_first)
        
        # Should be called once
        assert call_count == 1
        
        # Execute deferred functions on subsequent registration
        for deferred_func in bp.deferred_functions:
            deferred_func(state_subsequent)
        
        # Should still be called only once (not called on subsequent registration)
        assert call_count == 1
    finally:
        # Restore original method
        app.add_template_global = original_add_template_global
