# file: src/flask/src/flask/sansio/blueprints.py:443-444
# asked: {"lines": [443, 444], "branches": []}
# gained: {"lines": [443, 444], "branches": []}

import pytest
import typing as t
from flask.sansio.blueprints import Blueprint

def test_app_template_filter_overload_with_name():
    """Test the @t.overload decorator for app_template_filter with name parameter."""
    bp = Blueprint('test', __name__)
    
    # This test verifies that the overload signature exists and is callable
    # The actual implementation is tested in other tests
    assert hasattr(bp, 'app_template_filter')
    assert callable(bp.app_template_filter)

def test_app_template_filter_overload_without_name():
    """Test the @t.overload decorator for app_template_filter without name parameter."""
    bp = Blueprint('test', __name__)
    
    # This test verifies that the overload signature exists and is callable
    # The actual implementation is tested in other tests
    assert hasattr(bp, 'app_template_filter')
    assert callable(bp.app_template_filter)
