# file: src/flask/src/flask/sansio/blueprints.py:223-230
# asked: {"lines": [223, 224, 230], "branches": []}
# gained: {"lines": [223, 224, 230], "branches": []}

import pytest
from flask.sansio.blueprints import Blueprint

def test_blueprint_record_method():
    """Test that the record method correctly adds functions to deferred_functions list."""
    bp = Blueprint('test', __name__)
    
    # Create a mock function to record
    def mock_func(state):
        pass
    
    # Initially, deferred_functions should be empty
    assert len(bp.deferred_functions) == 0
    
    # Call the record method
    bp.record(mock_func)
    
    # Verify the function was added to deferred_functions
    assert len(bp.deferred_functions) == 1
    assert bp.deferred_functions[0] is mock_func
    
    # Test with multiple functions
    def mock_func2(state):
        pass
        
    bp.record(mock_func2)
    assert len(bp.deferred_functions) == 2
    assert bp.deferred_functions[1] is mock_func2

def test_blueprint_record_with_setupmethod_decorator():
    """Test that record method respects the setupmethod decorator behavior."""
    bp = Blueprint('test', __name__)
    
    # Create a mock function
    def mock_func(state):
        pass
    
    # Record should work when blueprint is not yet registered
    bp.record(mock_func)
    assert len(bp.deferred_functions) == 1
    
    # Simulate blueprint registration by setting _got_registered_once
    bp._got_registered_once = True
    
    # Now record should raise AssertionError due to setupmethod decorator
    with pytest.raises(AssertionError, match="The setup method 'record' can no longer be called on the blueprint 'test'"):
        bp.record(mock_func)
