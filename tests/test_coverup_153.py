# file: src/flask/src/flask/sansio/scaffold.py:264-269
# asked: {"lines": [264, 265, 266, 267, 269], "branches": [[266, 267], [266, 269]]}
# gained: {"lines": [264, 265, 266, 267, 269], "branches": [[266, 267], [266, 269]]}

import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffoldStaticUrlPathSetter:
    """Test cases for Scaffold.static_url_path setter to achieve full coverage."""
    
    def test_static_url_path_setter_with_none_value(self):
        """Test setting static_url_path to None."""
        scaffold = Scaffold("test_app")
        scaffold.static_url_path = None
        assert scaffold._static_url_path is None
    
    def test_static_url_path_setter_with_empty_string(self):
        """Test setting static_url_path to empty string."""
        scaffold = Scaffold("test_app")
        scaffold.static_url_path = ""
        assert scaffold._static_url_path == ""
    
    def test_static_url_path_setter_with_slash_only(self):
        """Test setting static_url_path to '/'."""
        scaffold = Scaffold("test_app")
        scaffold.static_url_path = "/"
        assert scaffold._static_url_path == ""
    
    def test_static_url_path_setter_with_trailing_slash(self):
        """Test setting static_url_path with trailing slash."""
        scaffold = Scaffold("test_app")
        scaffold.static_url_path = "/static/"
        assert scaffold._static_url_path == "/static"
    
    def test_static_url_path_setter_with_multiple_trailing_slashes(self):
        """Test setting static_url_path with multiple trailing slashes."""
        scaffold = Scaffold("test_app")
        scaffold.static_url_path = "/static///"
        assert scaffold._static_url_path == "/static"
    
    def test_static_url_path_setter_with_no_trailing_slash(self):
        """Test setting static_url_path without trailing slash."""
        scaffold = Scaffold("test_app")
        scaffold.static_url_path = "/static"
        assert scaffold._static_url_path == "/static"
