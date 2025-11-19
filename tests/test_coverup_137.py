# file: src/flask/src/flask/sansio/scaffold.py:271-282
# asked: {"lines": [271, 272, 279, 280, 282], "branches": [[279, 280], [279, 282]]}
# gained: {"lines": [271, 272, 279, 280, 282], "branches": [[279, 280], [279, 282]]}

import os
import pytest
from jinja2 import FileSystemLoader
from flask.sansio.scaffold import Scaffold

class TestScaffoldJinjaLoader:
    """Test cases for Scaffold.jinja_loader property."""
    
    def test_jinja_loader_with_template_folder(self, tmp_path):
        """Test jinja_loader returns FileSystemLoader when template_folder is set."""
        # Create a temporary directory structure
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        # Create a Scaffold instance with template_folder
        scaffold = Scaffold(
            import_name="test_app",
            template_folder="templates",
            root_path=str(tmp_path)
        )
        
        # Access the jinja_loader property
        loader = scaffold.jinja_loader
        
        # Verify it returns a FileSystemLoader
        assert isinstance(loader, FileSystemLoader)
        # Verify the loader points to the correct path
        expected_path = os.path.join(str(tmp_path), "templates")
        assert loader.searchpath == [expected_path]
    
    def test_jinja_loader_without_template_folder(self):
        """Test jinja_loader returns None when template_folder is not set."""
        # Create a Scaffold instance without template_folder
        scaffold = Scaffold(import_name="test_app")
        
        # Access the jinja_loader property
        loader = scaffold.jinja_loader
        
        # Verify it returns None
        assert loader is None
    
    def test_jinja_loader_cached_property(self):
        """Test that jinja_loader is properly cached."""
        scaffold = Scaffold(import_name="test_app")
        
        # First access should compute the value
        loader1 = scaffold.jinja_loader
        
        # Second access should return the cached value
        loader2 = scaffold.jinja_loader
        
        # Both should be the same object (cached)
        assert loader1 is loader2
        assert loader1 is None  # No template_folder set
