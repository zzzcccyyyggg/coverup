# file: src/flask/src/flask/sansio/blueprints.py:232-244
# asked: {"lines": [232, 233, 240, 241, 242, 244], "branches": [[241, 0], [241, 242]]}
# gained: {"lines": [232, 233, 240, 241, 242, 244], "branches": [[241, 0], [241, 242]]}

import pytest
from unittest.mock import Mock, MagicMock
from flask.sansio.blueprints import Blueprint

class TestBlueprintRecordOnce:
    def test_record_once_calls_func_on_first_registration(self):
        """Test that record_once calls the wrapped function when first_registration is True"""
        # Create a blueprint instance
        bp = Blueprint('test_bp', __name__)
        
        # Mock the function to be wrapped
        mock_func = Mock()
        
        # Call record_once with the mock function
        bp.record_once(mock_func)
        
        # Verify the function was added to deferred_functions
        assert len(bp.deferred_functions) == 1
        
        # Get the wrapper function that was recorded
        wrapper_func = bp.deferred_functions[0]
        
        # Create a mock state with first_registration=True
        mock_state = Mock()
        mock_state.first_registration = True
        
        # Call the wrapper function
        wrapper_func(mock_state)
        
        # Verify the original function was called with the state
        mock_func.assert_called_once_with(mock_state)
    
    def test_record_once_does_not_call_func_on_subsequent_registration(self):
        """Test that record_once does not call the wrapped function when first_registration is False"""
        # Create a blueprint instance
        bp = Blueprint('test_bp', __name__)
        
        # Mock the function to be wrapped
        mock_func = Mock()
        
        # Call record_once with the mock function
        bp.record_once(mock_func)
        
        # Verify the function was added to deferred_functions
        assert len(bp.deferred_functions) == 1
        
        # Get the wrapper function that was recorded
        wrapper_func = bp.deferred_functions[0]
        
        # Create a mock state with first_registration=False
        mock_state = Mock()
        mock_state.first_registration = False
        
        # Call the wrapper function
        wrapper_func(mock_state)
        
        # Verify the original function was NOT called
        mock_func.assert_not_called()
    
    def test_record_once_wrapper_preserves_metadata(self):
        """Test that update_wrapper preserves function metadata"""
        # Create a blueprint instance
        bp = Blueprint('test_bp', __name__)
        
        # Create a function with specific metadata
        def test_func(state):
            """Test function docstring"""
            pass
        
        test_func.some_attribute = "test_value"
        
        # Call record_once with the function
        bp.record_once(test_func)
        
        # Verify the function was added to deferred_functions
        assert len(bp.deferred_functions) == 1
        
        # Get the wrapper function
        wrapper_func = bp.deferred_functions[0]
        
        # Verify the wrapper preserves the original function's metadata
        assert wrapper_func.__name__ == test_func.__name__
        assert wrapper_func.__doc__ == test_func.__doc__
        assert hasattr(wrapper_func, 'some_attribute')
        assert wrapper_func.some_attribute == "test_value"
