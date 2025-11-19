# file: src/flask/src/flask/sansio/blueprints.py:475-495
# asked: {"lines": [493], "branches": []}
# gained: {"lines": [493], "branches": []}

import pytest
from flask.sansio.blueprints import Blueprint, BlueprintSetupState
from flask.sansio.app import App

def test_add_app_template_filter_executes_line_493():
    """Test that add_app_template_filter executes line 493 where state.app.add_template_filter is called."""
    
    # Create a mock app to track if add_template_filter is called
    class MockApp:
        def __init__(self):
            self.template_filters = {}
            
        def add_template_filter(self, f, name=None):
            self.template_filters[name or f.__name__] = f
    
    # Create blueprint and mock app
    blueprint = Blueprint('test', __name__)
    mock_app = MockApp()
    
    # Create a test filter function
    def test_filter(value):
        return value.upper()
    
    # Add the template filter to the blueprint
    blueprint.add_app_template_filter(test_filter, name='custom_filter')
    
    # Verify the deferred function was recorded
    assert len(blueprint.deferred_functions) == 1
    
    # Create a proper BlueprintSetupState object
    state = BlueprintSetupState(blueprint, mock_app, {}, True)
    
    # Execute the deferred function to trigger line 493
    blueprint.deferred_functions[0](state)
    
    # Verify that add_template_filter was called on the app
    assert 'custom_filter' in mock_app.template_filters
    assert mock_app.template_filters['custom_filter'] is test_filter

def test_add_app_template_filter_without_name():
    """Test add_app_template_filter without providing a name (uses function name)."""
    
    class MockApp:
        def __init__(self):
            self.template_filters = {}
            
        def add_template_filter(self, f, name=None):
            self.template_filters[name or f.__name__] = f
    
    blueprint = Blueprint('test', __name__)
    mock_app = MockApp()
    
    def another_filter(value):
        return value.lower()
    
    # Add template filter without name
    blueprint.add_app_template_filter(another_filter)
    
    # Create proper BlueprintSetupState and execute the deferred function
    state = BlueprintSetupState(blueprint, mock_app, {}, True)
    blueprint.deferred_functions[0](state)
    
    # Verify filter was registered with function name
    assert 'another_filter' in mock_app.template_filters
    assert mock_app.template_filters['another_filter'] is another_filter

def test_add_app_template_filter_multiple_filters():
    """Test adding multiple template filters to ensure each executes line 493."""
    
    class MockApp:
        def __init__(self):
            self.template_filters = {}
            self.add_template_filter_call_count = 0
            
        def add_template_filter(self, f, name=None):
            self.template_filters[name or f.__name__] = f
            self.add_template_filter_call_count += 1
    
    blueprint = Blueprint('test', __name__)
    mock_app = MockApp()
    
    def filter1(value):
        return value + "_1"
    
    def filter2(value):
        return value + "_2"
    
    # Add multiple filters
    blueprint.add_app_template_filter(filter1, name='filter_one')
    blueprint.add_app_template_filter(filter2, name='filter_two')
    
    # Verify two deferred functions were recorded
    assert len(blueprint.deferred_functions) == 2
    
    # Execute all deferred functions with proper BlueprintSetupState
    state = BlueprintSetupState(blueprint, mock_app, {}, True)
    for deferred_func in blueprint.deferred_functions:
        deferred_func(state)
    
    # Verify both filters were registered and line 493 executed twice
    assert mock_app.add_template_filter_call_count == 2
    assert 'filter_one' in mock_app.template_filters
    assert 'filter_two' in mock_app.template_filters
    assert mock_app.template_filters['filter_one'] is filter1
    assert mock_app.template_filters['filter_two'] is filter2
