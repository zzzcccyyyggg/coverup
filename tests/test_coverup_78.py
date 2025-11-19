# file: src/flask/src/flask/sansio/blueprints.py:503-529
# asked: {"lines": [503, 504, 505, 521, 522, 523, 525, 526, 527, 529], "branches": [[521, 522], [521, 525]]}
# gained: {"lines": [503, 504, 505, 521, 522, 523, 525, 526, 527, 529], "branches": [[521, 522], [521, 525]]}

import pytest
from flask.sansio.blueprints import Blueprint

def test_app_template_test_with_name():
    """Test app_template_test decorator with explicit name parameter."""
    bp = Blueprint('test_bp', __name__)
    
    @bp.app_template_test('custom_test')
    def is_even(value):
        return value % 2 == 0
    
    # Verify the decorator returns the function
    assert callable(is_even)
    assert is_even(2) is True
    assert is_even(3) is False

def test_app_template_test_without_name():
    """Test app_template_test decorator without name parameter (using function name)."""
    bp = Blueprint('test_bp', __name__)
    
    @bp.app_template_test()
    def is_odd(value):
        return value % 2 == 1
    
    # Verify the decorator returns the function
    assert callable(is_odd)
    assert is_odd(1) is True
    assert is_odd(2) is False

def test_app_template_test_direct_call():
    """Test app_template_test when called directly with a function (lines 521-523)."""
    bp = Blueprint('test_bp', __name__)
    
    def is_positive(value):
        return value > 0
    
    # Call app_template_test directly with the function (no decorator syntax)
    result = bp.app_template_test(is_positive)
    
    # Should return the same function
    assert result is is_positive
    assert callable(result)
    assert result(5) is True
    assert result(-1) is False
