# file: src/flask/src/flask/sansio/scaffold.py:233-238
# asked: {"lines": [233, 234, 235, 236, 238], "branches": [[235, 236], [235, 238]]}
# gained: {"lines": [233, 234, 235, 236, 238], "branches": [[235, 236], [235, 238]]}

import os
import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffoldStaticFolderSetter:
    def test_static_folder_setter_with_none_value(self):
        """Test that static_folder setter handles None value correctly."""
        scaffold = Scaffold(__name__)
        scaffold.static_folder = None
        assert scaffold._static_folder is None

    def test_static_folder_setter_with_string_value(self):
        """Test that static_folder setter processes string value correctly."""
        scaffold = Scaffold(__name__)
        scaffold.static_folder = "/static/"
        assert scaffold._static_folder == "/static"

    def test_static_folder_setter_with_pathlike_value(self):
        """Test that static_folder setter processes PathLike value correctly."""
        scaffold = Scaffold(__name__)
        
        class MockPathLike:
            def __init__(self, path):
                self.path = path
            
            def __fspath__(self):
                return self.path
        
        path = MockPathLike("/static/")
        scaffold.static_folder = path
        assert scaffold._static_folder == "/static"

    def test_static_folder_setter_with_backslash_path(self):
        """Test that static_folder setter handles backslash paths correctly."""
        scaffold = Scaffold(__name__)
        scaffold.static_folder = "\\static\\"
        assert scaffold._static_folder == "\\static"

    def test_static_folder_setter_with_mixed_slashes(self):
        """Test that static_folder setter handles mixed slash paths correctly."""
        scaffold = Scaffold(__name__)
        scaffold.static_folder = "/static\\"
        assert scaffold._static_folder == "/static"
