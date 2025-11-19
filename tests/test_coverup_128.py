# file: src/flask/src/flask/sansio/scaffold.py:223-231
# asked: {"lines": [223, 224, 228, 229, 231], "branches": [[228, 229], [228, 231]]}
# gained: {"lines": [223, 224, 228, 229, 231], "branches": [[228, 229], [228, 231]]}

import os
import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffoldStaticFolder:
    """Test cases for Scaffold.static_folder property"""
    
    def test_static_folder_with_static_folder_set(self, tmp_path):
        """Test static_folder property when _static_folder is set"""
        # Create a temporary directory structure
        root_path = tmp_path / "test_app"
        root_path.mkdir()
        static_folder = "static"
        static_path = root_path / static_folder
        static_path.mkdir()
        
        scaffold = Scaffold(__name__, root_path=str(root_path))
        scaffold._static_folder = static_folder
        
        result = scaffold.static_folder
        
        expected_path = os.path.join(str(root_path), static_folder)
        assert result == expected_path
    
    def test_static_folder_without_static_folder_set(self):
        """Test static_folder property when _static_folder is None"""
        scaffold = Scaffold(__name__)
        scaffold._static_folder = None
        
        result = scaffold.static_folder
        
        assert result is None
