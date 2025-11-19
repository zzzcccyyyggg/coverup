# file: src/click/src/click/termui.py:816-843
# asked: {"lines": [816, 838, 839, 841, 843], "branches": [[838, 839], [838, 843]]}
# gained: {"lines": [816, 838, 839, 841, 843], "branches": [[838, 839], [838, 843]]}

import pytest
from click.termui import getchar
from unittest.mock import Mock, patch

class TestGetchar:
    def test_getchar_first_call_imports_implementation(self, monkeypatch):
        """Test that getchar imports the implementation on first call"""
        # Mock the global _getchar to be None initially
        monkeypatch.setattr('click.termui._getchar', None)
        
        # Mock the imported getchar function from click._termui_impl
        mock_impl = Mock(return_value='a')
        with patch('click._termui_impl.getchar', mock_impl):
            # Call getchar for the first time
            result = getchar(echo=False)
            
            # Verify the implementation was imported and called
            mock_impl.assert_called_once_with(False)
            assert result == 'a'
    
    def test_getchar_subsequent_calls_use_cached_implementation(self, monkeypatch):
        """Test that subsequent getchar calls use the cached implementation"""
        # Mock the global _getchar to be already set
        mock_cached = Mock(return_value='b')
        monkeypatch.setattr('click.termui._getchar', mock_cached)
        
        # Call getchar multiple times
        result1 = getchar(echo=True)
        result2 = getchar(echo=False)
        
        # Verify the cached implementation was called multiple times
        assert mock_cached.call_count == 2
        mock_cached.assert_any_call(True)
        mock_cached.assert_any_call(False)
        assert result1 == 'b'
        assert result2 == 'b'
    
    def test_getchar_with_echo_true(self, monkeypatch):
        """Test getchar with echo=True parameter"""
        monkeypatch.setattr('click.termui._getchar', None)
        
        mock_impl = Mock(return_value='c')
        with patch('click._termui_impl.getchar', mock_impl):
            result = getchar(echo=True)
            
            mock_impl.assert_called_once_with(True)
            assert result == 'c'
    
    def test_getchar_with_echo_false(self, monkeypatch):
        """Test getchar with echo=False parameter"""
        monkeypatch.setattr('click.termui._getchar', None)
        
        mock_impl = Mock(return_value='d')
        with patch('click._termui_impl.getchar', mock_impl):
            result = getchar(echo=False)
            
            mock_impl.assert_called_once_with(False)
            assert result == 'd'
