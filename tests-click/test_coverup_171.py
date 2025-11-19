# file: src/click/src/click/core.py:116-140
# asked: {"lines": [116, 132, 133, 134, 135, 136, 138, 140], "branches": []}
# gained: {"lines": [116, 132, 133, 134, 135, 136, 138, 140], "branches": []}

import pytest
from click.core import Parameter
import collections.abc as cabc

class MockParameter:
    def __init__(self, name, is_eager=False):
        self.name = name
        self.is_eager = is_eager
    
    def __repr__(self):
        return f"MockParameter({self.name}, is_eager={self.is_eager})"

def test_iter_params_for_processing_empty_lists():
    """Test with empty invocation and declaration orders."""
    from click.core import iter_params_for_processing
    
    result = iter_params_for_processing([], [])
    assert result == []

def test_iter_params_for_processing_all_in_invocation():
    """Test when all declared parameters are in invocation order."""
    from click.core import iter_params_for_processing
    
    param1 = MockParameter("param1", is_eager=False)
    param2 = MockParameter("param2", is_eager=True)
    param3 = MockParameter("param3", is_eager=False)
    
    declaration_order = [param1, param2, param3]
    invocation_order = [param3, param1, param2]  # Different order
    
    result = iter_params_for_processing(invocation_order, declaration_order)
    
    # Should be sorted by: eager first, then by invocation order index
    assert result == [param2, param3, param1]

def test_iter_params_for_processing_some_missing_from_invocation():
    """Test when some declared parameters are not in invocation order."""
    from click.core import iter_params_for_processing
    
    param1 = MockParameter("param1", is_eager=False)
    param2 = MockParameter("param2", is_eager=True)
    param3 = MockParameter("param3", is_eager=False)
    param4 = MockParameter("param4", is_eager=True)  # Not in invocation order
    
    declaration_order = [param1, param2, param3, param4]
    invocation_order = [param3, param1, param2]  # param4 missing
    
    result = iter_params_for_processing(invocation_order, declaration_order)
    
    # Eager params first (param2, param4), then by invocation order index
    # param4 has infinite index, so comes after all invocation order params
    assert result == [param2, param4, param3, param1]

def test_iter_params_for_processing_none_in_invocation():
    """Test when no declared parameters are in invocation order."""
    from click.core import iter_params_for_processing
    
    param1 = MockParameter("param1", is_eager=True)
    param2 = MockParameter("param2", is_eager=False)
    param3 = MockParameter("param3", is_eager=True)
    
    declaration_order = [param1, param2, param3]
    invocation_order = []  # Empty invocation order
    
    result = iter_params_for_processing(invocation_order, declaration_order)
    
    # Should be sorted by eagerness only (all have infinite index)
    assert result == [param1, param3, param2]

def test_iter_params_for_processing_mixed_eagerness():
    """Test with mixed eager and non-eager parameters."""
    from click.core import iter_params_for_processing
    
    eager1 = MockParameter("eager1", is_eager=True)
    eager2 = MockParameter("eager2", is_eager=True)
    non_eager1 = MockParameter("non_eager1", is_eager=False)
    non_eager2 = MockParameter("non_eager2", is_eager=False)
    
    declaration_order = [eager1, non_eager1, eager2, non_eager2]
    invocation_order = [non_eager2, eager1, non_eager1, eager2]
    
    result = iter_params_for_processing(invocation_order, declaration_order)
    
    # Eager params first (eager1, eager2), then by invocation order index
    assert result == [eager1, eager2, non_eager2, non_eager1]
