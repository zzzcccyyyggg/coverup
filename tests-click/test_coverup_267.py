# file: src/click/src/click/termui.py:54-57
# asked: {"lines": [54, 55, 57], "branches": []}
# gained: {"lines": [54, 55, 57], "branches": []}

import pytest
from click.termui import hidden_prompt_func
from unittest.mock import patch, MagicMock

def test_hidden_prompt_func_calls_getpass():
    """Test that hidden_prompt_func calls getpass.getpass with the prompt."""
    test_prompt = "Enter password: "
    expected_result = "secret123"
    
    with patch('getpass.getpass') as mock_getpass:
        mock_getpass.return_value = expected_result
        
        result = hidden_prompt_func(test_prompt)
        
        mock_getpass.assert_called_once_with(test_prompt)
        assert result == expected_result

def test_hidden_prompt_func_imports_getpass():
    """Test that hidden_prompt_func imports getpass module internally."""
    # This test ensures the import statement is executed
    with patch('getpass.getpass') as mock_getpass:
        mock_getpass.return_value = "test"
        
        # Call the function which should trigger the import
        result = hidden_prompt_func("test prompt")
        
        # Verify getpass was called and result is correct
        mock_getpass.assert_called_once_with("test prompt")
        assert result == "test"
