# file: src/click/src/click/termui.py:846-849
# asked: {"lines": [846, 847, 849], "branches": []}
# gained: {"lines": [846, 847, 849], "branches": []}

import pytest
from click.termui import raw_terminal
from unittest.mock import patch, MagicMock

def test_raw_terminal():
    """Test that raw_terminal imports and returns the function from _termui_impl."""
    mock_context_manager = MagicMock()
    
    with patch('click._termui_impl.raw_terminal', return_value=mock_context_manager) as mock_impl:
        result = raw_terminal()
        
        # Verify the function was called
        mock_impl.assert_called_once()
        
        # Verify the result is what we expect
        assert result == mock_context_manager
