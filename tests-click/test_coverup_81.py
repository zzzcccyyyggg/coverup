# file: src/click/src/click/types.py:955-966
# asked: {"lines": [955, 958, 959, 960, 961, 962, 964, 966], "branches": [[958, 959], [958, 966], [959, 960], [959, 961], [961, 962], [961, 964]]}
# gained: {"lines": [955, 958, 959, 960, 961, 962, 964, 966], "branches": [[958, 959], [958, 966], [959, 960], [959, 961], [961, 962], [961, 964]]}

import os
import pytest
from pathlib import Path as PathLibPath
from click.types import Path


class TestPathCoercePathResult:
    """Test cases for Path.coerce_path_result method to achieve full coverage."""
    
    def test_coerce_path_result_with_str_type_and_bytes_value(self, monkeypatch):
        """Test when self.type is str and value is bytes."""
        path_type = Path(path_type=str)
        value = b"test_path"
        
        # Mock os.fsdecode to verify it's called
        def mock_fsdecode(val):
            assert val == value
            return "decoded_path"
        
        monkeypatch.setattr(os, "fsdecode", mock_fsdecode)
        
        result = path_type.coerce_path_result(value)
        assert result == "decoded_path"
    
    def test_coerce_path_result_with_bytes_type_and_str_value(self, monkeypatch):
        """Test when self.type is bytes and value is str."""
        path_type = Path(path_type=bytes)
        value = "test_path"
        
        # Mock os.fsencode to verify it's called
        def mock_fsencode(val):
            assert val == value
            return b"encoded_path"
        
        monkeypatch.setattr(os, "fsencode", mock_fsencode)
        
        result = path_type.coerce_path_result(value)
        assert result == b"encoded_path"
    
    def test_coerce_path_result_with_custom_type(self):
        """Test when self.type is a custom type (e.g., pathlib.Path)."""
        path_type = Path(path_type=PathLibPath)
        value = "test_path"
        
        result = path_type.coerce_path_result(value)
        assert result == PathLibPath(value)
        assert isinstance(result, PathLibPath)
    
    def test_coerce_path_result_with_same_type(self):
        """Test when value is already of the correct type."""
        # Test with str type and str value
        path_type = Path(path_type=str)
        value = "test_path"
        result = path_type.coerce_path_result(value)
        assert result == value
        
        # Test with bytes type and bytes value  
        path_type = Path(path_type=bytes)
        value = b"test_path"
        result = path_type.coerce_path_result(value)
        assert result == value
        
        # Test with pathlib.Path type and pathlib.Path value
        path_type = Path(path_type=PathLibPath)
        value = PathLibPath("test_path")
        result = path_type.coerce_path_result(value)
        assert result == value
    
    def test_coerce_path_result_with_none_type(self):
        """Test when self.type is None (should return value unchanged)."""
        path_type = Path(path_type=None)
        value = "test_path"
        
        result = path_type.coerce_path_result(value)
        assert result == value
