# file: src/click/src/click/types.py:943-953
# asked: {"lines": [943, 944, 945, 946, 947, 948, 949, 950, 951, 953], "branches": []}
# gained: {"lines": [943, 944, 945, 946, 947, 948, 949, 950, 951, 953], "branches": []}

import pytest
import click
from click.types import Path


class TestPathToInfoDict:
    def test_to_info_dict_returns_all_properties(self):
        """Test that to_info_dict returns all Path-specific properties."""
        path_type = Path(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=False,
            allow_dash=True,
            resolve_path=True,
            executable=True,
            path_type=str
        )
        
        info_dict = path_type.to_info_dict()
        
        assert info_dict["exists"] is True
        assert info_dict["file_okay"] is False
        assert info_dict["dir_okay"] is True
        assert info_dict["writable"] is True
        assert info_dict["readable"] is False
        assert info_dict["allow_dash"] is True
        assert info_dict["name"] == "directory"  # When file_okay=False and dir_okay=True
        assert info_dict["param_type"] == "Path"

    def test_to_info_dict_with_default_values(self):
        """Test to_info_dict with default Path constructor values."""
        path_type = Path()
        
        info_dict = path_type.to_info_dict()
        
        assert info_dict["exists"] is False
        assert info_dict["file_okay"] is True
        assert info_dict["dir_okay"] is True
        assert info_dict["writable"] is False
        assert info_dict["readable"] is True
        assert info_dict["allow_dash"] is False
        assert info_dict["name"] == "path"  # Default name when both file_okay and dir_okay are True
        assert info_dict["param_type"] == "Path"

    def test_to_info_dict_includes_superclass_info(self):
        """Test that to_info_dict includes information from ParamType superclass."""
        path_type = Path()
        
        info_dict = path_type.to_info_dict()
        
        # Check that superclass information is included
        assert "name" in info_dict
        assert "param_type" in info_dict
        assert info_dict["param_type"] == "Path"
        assert info_dict["name"] == "path"  # Default name when both file_okay and dir_okay are True

    def test_to_info_dict_file_only_path(self):
        """Test to_info_dict for a file-only path type."""
        path_type = Path(file_okay=True, dir_okay=False)
        
        info_dict = path_type.to_info_dict()
        
        assert info_dict["file_okay"] is True
        assert info_dict["dir_okay"] is False
        assert info_dict["name"] == "file"  # When file_okay=True and dir_okay=False
        assert info_dict["param_type"] == "Path"

    def test_to_info_dict_directory_only_path(self):
        """Test to_info_dict for a directory-only path type."""
        path_type = Path(file_okay=False, dir_okay=True)
        
        info_dict = path_type.to_info_dict()
        
        assert info_dict["file_okay"] is False
        assert info_dict["dir_okay"] is True
        assert info_dict["name"] == "directory"  # When file_okay=False and dir_okay=True
        assert info_dict["param_type"] == "Path"
