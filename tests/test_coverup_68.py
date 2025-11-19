# file: src/flask/src/flask/sansio/scaffold.py:248-262
# asked: {"lines": [248, 249, 255, 256, 258, 259, 260, 262], "branches": [[255, 256], [255, 258], [258, 259], [258, 262]]}
# gained: {"lines": [248, 249, 255, 256, 258, 259, 260, 262], "branches": [[255, 256], [255, 258], [258, 259], [258, 262]]}

import pytest
import os
import tempfile
from flask.sansio.scaffold import Scaffold

class TestScaffoldStaticUrlPath:
    """Test cases for Scaffold.static_url_path property to achieve full coverage."""
    
    def test_static_url_path_explicitly_set(self):
        """Test when _static_url_path is explicitly set."""
        scaffold = Scaffold(__name__)
        scaffold._static_url_path = "/custom/static"
        assert scaffold.static_url_path == "/custom/static"
    
    def test_static_url_path_derived_from_static_folder(self):
        """Test when static_url_path is derived from static_folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            scaffold = Scaffold(__name__, static_folder=temp_dir)
            basename = os.path.basename(temp_dir)
            expected_path = f"/{basename}".rstrip("/")
            assert scaffold.static_url_path == expected_path
    
    def test_static_url_path_derived_from_static_folder_with_trailing_slash(self):
        """Test when static_folder has trailing slash in path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            folder_with_slash = temp_dir + "/"
            scaffold = Scaffold(__name__, static_folder=folder_with_slash)
            basename = os.path.basename(temp_dir)
            expected_path = f"/{basename}".rstrip("/")
            assert scaffold.static_url_path == expected_path
    
    def test_static_url_path_none_when_no_static_folder(self):
        """Test when neither static_url_path nor static_folder are set."""
        scaffold = Scaffold(__name__)
        assert scaffold.static_url_path is None
