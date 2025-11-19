# file: src/flask/src/flask/sansio/blueprints.py:449-473
# asked: {"lines": [449, 450, 451, 465, 466, 467, 469, 470, 471, 473], "branches": [[465, 466], [465, 469]]}
# gained: {"lines": [449, 450, 451, 465, 466, 467, 469, 470, 471, 473], "branches": [[465, 466], [465, 469]]}

import pytest
from flask.sansio.blueprints import Blueprint

def test_blueprint_app_template_filter_without_name():
    """Test app_template_filter decorator without name parameter."""
    bp = Blueprint('test', __name__)
    
    @bp.app_template_filter()
    def test_filter(value):
        return value.upper()
    
    # Verify the filter was registered
    assert len(bp.deferred_functions) == 1
    
    # Clean up
    bp.deferred_functions.clear()

def test_blueprint_app_template_filter_with_name():
    """Test app_template_filter decorator with name parameter."""
    bp = Blueprint('test', __name__)
    
    @bp.app_template_filter('custom_name')
    def test_filter(value):
        return value.upper()
    
    # Verify the filter was registered
    assert len(bp.deferred_functions) == 1
    
    # Clean up
    bp.deferred_functions.clear()

def test_blueprint_app_template_filter_callable_name():
    """Test app_template_filter when name parameter is callable (direct usage)."""
    bp = Blueprint('test', __name__)
    
    def test_filter(value):
        return value.upper()
    
    # Direct call with callable as name parameter (lines 465-467)
    result = bp.app_template_filter(test_filter)
    
    # Should return the same function
    assert result is test_filter
    
    # Verify the filter was registered
    assert len(bp.deferred_functions) == 1
    
    # Clean up
    bp.deferred_functions.clear()
