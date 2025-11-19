# file: src/flask/src/flask/sansio/blueprints.py:531-553
# asked: {"lines": [531, 532, 533, 550, 551, 553], "branches": []}
# gained: {"lines": [531, 532, 533, 550, 551, 553], "branches": []}

import pytest
from flask import Flask, Blueprint
from flask.sansio.blueprints import BlueprintSetupState

def test_add_app_template_test_with_name():
    """Test add_app_template_test with explicit name parameter."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    def custom_test(value):
        return value == 'test'
    
    # Register the template test with explicit name
    bp.add_app_template_test(custom_test, name='custom_test_name')
    
    # Create a mock state to test the deferred function
    state = BlueprintSetupState(bp, app, {}, True)
    
    # Manually call the deferred function that was registered
    assert len(bp.deferred_functions) == 1
    deferred_func = bp.deferred_functions[0]
    deferred_func(state)
    
    # Verify the test was registered in the app's jinja environment
    assert 'custom_test_name' in app.jinja_env.tests
    assert app.jinja_env.tests['custom_test_name'] is custom_test

def test_add_app_template_test_without_name():
    """Test add_app_template_test without name parameter (uses function name)."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    def custom_test(value):
        return value == 'test'
    
    # Register the template test without explicit name
    bp.add_app_template_test(custom_test)
    
    # Create a mock state to test the deferred function
    state = BlueprintSetupState(bp, app, {}, True)
    
    # Manually call the deferred function that was registered
    assert len(bp.deferred_functions) == 1
    deferred_func = bp.deferred_functions[0]
    deferred_func(state)
    
    # Verify the test was registered with function name
    assert 'custom_test' in app.jinja_env.tests
    assert app.jinja_env.tests['custom_test'] is custom_test

def test_add_app_template_test_decorator_usage():
    """Test add_app_template_test via the decorator interface."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    # Use the decorator form
    @bp.app_template_test('decorator_test')
    def custom_test(value):
        return value == 'decorator'
    
    # Create a mock state to test the deferred function
    state = BlueprintSetupState(bp, app, {}, True)
    
    # Manually call the deferred function that was registered
    assert len(bp.deferred_functions) == 1
    deferred_func = bp.deferred_functions[0]
    deferred_func(state)
    
    # Verify the test was registered
    assert 'decorator_test' in app.jinja_env.tests
    assert app.jinja_env.tests['decorator_test'] is custom_test

def test_add_app_template_test_functionality():
    """Test that the registered template test actually works."""
    app = Flask(__name__)
    bp = Blueprint('test_bp', __name__)
    
    def is_even(value):
        return value % 2 == 0
    
    bp.add_app_template_test(is_even, name='even')
    
    # Create a mock state to test the deferred function
    state = BlueprintSetupState(bp, app, {}, True)
    
    # Manually call the deferred function that was registered
    assert len(bp.deferred_functions) == 1
    deferred_func = bp.deferred_functions[0]
    deferred_func(state)
    
    # Test the functionality
    assert app.jinja_env.tests['even'](2) is True
    assert app.jinja_env.tests['even'](3) is False
