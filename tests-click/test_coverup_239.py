# file: src/click/src/click/types.py:801-804
# asked: {"lines": [801, 802, 803, 804], "branches": []}
# gained: {"lines": [801, 802, 803, 804], "branches": []}

import pytest
from click.types import File

class TestFileToInfoDict:
    def test_to_info_dict_includes_mode_and_encoding(self):
        """Test that File.to_info_dict() includes mode and encoding in the returned dict."""
        file_type = File(mode='r', encoding='utf-8')
        info_dict = file_type.to_info_dict()
        
        assert 'mode' in info_dict
        assert 'encoding' in info_dict
        assert info_dict['mode'] == 'r'
        assert info_dict['encoding'] == 'utf-8'
        
    def test_to_info_dict_with_none_encoding(self):
        """Test that File.to_info_dict() handles None encoding correctly."""
        file_type = File(mode='wb', encoding=None)
        info_dict = file_type.to_info_dict()
        
        assert 'mode' in info_dict
        assert 'encoding' in info_dict
        assert info_dict['mode'] == 'wb'
        assert info_dict['encoding'] is None
        
    def test_to_info_dict_with_different_modes(self):
        """Test that File.to_info_dict() works with various file modes."""
        test_modes = ['r', 'w', 'a', 'rb', 'wb', 'ab', 'r+', 'w+', 'a+']
        
        for mode in test_modes:
            file_type = File(mode=mode, encoding='latin-1')
            info_dict = file_type.to_info_dict()
            
            assert info_dict['mode'] == mode
            assert info_dict['encoding'] == 'latin-1'
