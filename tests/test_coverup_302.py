# file: src/flask/src/flask/sansio/blueprints.py:379-410
# asked: {"lines": [400], "branches": [[399, 400]]}
# gained: {"lines": [400], "branches": [[399, 400]]}

import pytest
from collections import defaultdict
from flask.sansio.blueprints import Blueprint
from flask.sansio.app import App

def test_merge_blueprint_funcs_view_functions():
    """Test that view functions are properly merged from blueprint to app."""
    # Create a minimal App instance with all required Scaffold attributes
    app = App.__new__(App)
    app.view_functions = {}
    app.error_handler_spec = defaultdict(lambda: defaultdict(dict))
    app.before_request_funcs = defaultdict(list)
    app.after_request_funcs = defaultdict(list)
    app.teardown_request_funcs = defaultdict(list)
    app.url_default_functions = defaultdict(list)
    app.url_value_preprocessors = defaultdict(list)
    app.template_context_processors = defaultdict(list)
    
    bp = Blueprint('test_bp', __name__)
    
    # Add a view function to the blueprint
    def view_func():
        return "Hello from blueprint"
    
    # Manually add to view_functions since add_url_rule requires setup
    bp.view_functions['test_endpoint'] = view_func
    
    # Verify the blueprint has the view function
    assert 'test_endpoint' in bp.view_functions
    assert bp.view_functions['test_endpoint'] == view_func
    
    # Verify the app does not have the view function initially
    assert 'test_endpoint' not in app.view_functions
    
    # Call the method that should merge view functions
    bp._merge_blueprint_funcs(app, bp.name)
    
    # Verify the view function was copied to the app
    assert 'test_endpoint' in app.view_functions
    assert app.view_functions['test_endpoint'] == view_func

def test_merge_blueprint_funcs_multiple_view_functions():
    """Test that multiple view functions are properly merged from blueprint to app."""
    # Create a minimal App instance with all required Scaffold attributes
    app = App.__new__(App)
    app.view_functions = {}
    app.error_handler_spec = defaultdict(lambda: defaultdict(dict))
    app.before_request_funcs = defaultdict(list)
    app.after_request_funcs = defaultdict(list)
    app.teardown_request_funcs = defaultdict(list)
    app.url_default_functions = defaultdict(list)
    app.url_value_preprocessors = defaultdict(list)
    app.template_context_processors = defaultdict(list)
    
    bp = Blueprint('test_bp', __name__)
    
    # Add multiple view functions to the blueprint
    def view_func1():
        return "View 1"
    
    def view_func2():
        return "View 2"
    
    # Manually add to view_functions since add_url_rule requires setup
    bp.view_functions['test_endpoint1'] = view_func1
    bp.view_functions['test_endpoint2'] = view_func2
    
    # Verify the blueprint has the view functions
    assert 'test_endpoint1' in bp.view_functions
    assert 'test_endpoint2' in bp.view_functions
    
    # Call the method that should merge view functions
    bp._merge_blueprint_funcs(app, bp.name)
    
    # Verify all view functions were copied to the app
    assert 'test_endpoint1' in app.view_functions
    assert 'test_endpoint2' in app.view_functions
    assert app.view_functions['test_endpoint1'] == view_func1
    assert app.view_functions['test_endpoint2'] == view_func2

def test_merge_blueprint_funcs_empty_view_functions():
    """Test that _merge_blueprint_funcs works when blueprint has no view functions."""
    # Create a minimal App instance with all required Scaffold attributes
    app = App.__new__(App)
    app.view_functions = {}
    app.error_handler_spec = defaultdict(lambda: defaultdict(dict))
    app.before_request_funcs = defaultdict(list)
    app.after_request_funcs = defaultdict(list)
    app.teardown_request_funcs = defaultdict(list)
    app.url_default_functions = defaultdict(list)
    app.url_value_preprocessors = defaultdict(list)
    app.template_context_processors = defaultdict(list)
    
    bp = Blueprint('test_bp', __name__)
    
    # Verify the blueprint has no view functions initially
    assert len(bp.view_functions) == 0
    
    # Call the method - should not raise any errors
    bp._merge_blueprint_funcs(app, bp.name)
    
    # Verify the app still has no view functions
    assert len(app.view_functions) == 0
