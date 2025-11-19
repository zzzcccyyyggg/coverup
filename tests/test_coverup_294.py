# file: src/flask/src/flask/cli.py:867-879
# asked: {"lines": [876, 878, 879], "branches": []}
# gained: {"lines": [876, 878, 879], "branches": []}

import pytest
import click
import typing as t
from flask.cli import SeparatedPathType


class TestSeparatedPathType:
    """Test cases for SeparatedPathType class."""

    def test_convert_with_multiple_paths(self, monkeypatch):
        """Test convert method with multiple paths separated by OS path separator."""
        # Mock the split_envvar_value to return multiple items
        def mock_split_envvar_value(value):
            return value.split(';')
        
        # Create instance and patch the split_envvar_value method
        path_type = SeparatedPathType()
        monkeypatch.setattr(path_type, 'split_envvar_value', mock_split_envvar_value)
        
        # Mock the parent convert method to return the input value
        # Note: The actual call uses super_convert which is bound to the instance
        def mock_convert(self, value, param, ctx):
            return value
        
        monkeypatch.setattr(click.Path, 'convert', mock_convert)
        
        # Test with multiple paths
        test_value = "path1;path2;path3"
        result = path_type.convert(test_value, None, None)
        
        # Verify the result is a list of converted values
        assert result == ["path1", "path2", "path3"]
    
    def test_convert_with_single_path(self, monkeypatch):
        """Test convert method with a single path."""
        # Mock the split_envvar_value to return single item
        def mock_split_envvar_value(value):
            return [value]
        
        # Create instance and patch the split_envvar_value method
        path_type = SeparatedPathType()
        monkeypatch.setattr(path_type, 'split_envvar_value', mock_split_envvar_value)
        
        # Mock the parent convert method to return the input value
        def mock_convert(self, value, param, ctx):
            return value
        
        monkeypatch.setattr(click.Path, 'convert', mock_convert)
        
        # Test with single path
        test_value = "single_path"
        result = path_type.convert(test_value, None, None)
        
        # Verify the result is a list with one converted value
        assert result == ["single_path"]
    
    def test_convert_with_empty_string(self, monkeypatch):
        """Test convert method with empty string."""
        # Mock the split_envvar_value to return empty list
        def mock_split_envvar_value(value):
            return []
        
        # Create instance and patch the split_envvar_value method
        path_type = SeparatedPathType()
        monkeypatch.setattr(path_type, 'split_envvar_value', mock_split_envvar_value)
        
        # Mock the parent convert method (should not be called)
        def mock_convert(self, value, param, ctx):
            return value
        
        monkeypatch.setattr(click.Path, 'convert', mock_convert)
        
        # Test with empty string
        test_value = ""
        result = path_type.convert(test_value, None, None)
        
        # Verify the result is an empty list
        assert result == []
