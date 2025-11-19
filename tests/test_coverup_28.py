# file: src/flask/src/flask/cli.py:200-226
# asked: {"lines": [200, 204, 206, 207, 208, 210, 211, 213, 216, 217, 218, 220, 221, 223, 224, 226], "branches": [[207, 208], [207, 210], [210, 211], [210, 213], [216, 217], [220, 216], [220, 221], [223, 224], [223, 226]]}
# gained: {"lines": [200, 204, 206, 207, 208, 210, 211, 213, 216, 217, 218, 220, 221, 223, 224, 226], "branches": [[207, 208], [207, 210], [210, 211], [210, 213], [216, 217], [220, 216], [220, 221], [223, 224], [223, 226]]}

import os
import sys
import tempfile
import pytest
from flask.cli import prepare_import

class TestPrepareImport:
    
    def test_prepare_import_with_py_extension(self, monkeypatch):
        """Test that .py extension is removed from path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test_module.py")
            with open(test_file, "w") as f:
                f.write("# test file")
            
            result = prepare_import(test_file)
            assert result == "test_module"
    
    def test_prepare_import_with_init_file(self, monkeypatch):
        """Test path ending with __init__ is handled correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_dir = os.path.join(tmpdir, "package")
            os.makedirs(init_dir)
            init_file = os.path.join(init_dir, "__init__")
            with open(init_file, "w") as f:
                f.write("# init file")
            
            result = prepare_import(init_file)
            assert result == "package"
    
    def test_prepare_import_with_package_structure(self, monkeypatch):
        """Test package structure with __init__.py files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested package structure
            nested_dir = os.path.join(tmpdir, "outer", "inner")
            os.makedirs(nested_dir)
            
            # Create __init__.py files
            outer_init = os.path.join(tmpdir, "outer", "__init__.py")
            inner_init = os.path.join(nested_dir, "__init__.py")
            
            with open(outer_init, "w") as f:
                f.write("# outer init")
            with open(inner_init, "w") as f:
                f.write("# inner init")
            
            test_file = os.path.join(nested_dir, "module.py")
            with open(test_file, "w") as f:
                f.write("# test module")
            
            original_sys_path = sys.path.copy()
            
            try:
                result = prepare_import(test_file)
                assert result == "outer.inner.module"
                # The function should add the parent directory (tmpdir) to sys.path, not the outer directory
                assert tmpdir in sys.path
            finally:
                # Clean up sys.path
                sys.path[:] = original_sys_path
    
    def test_prepare_import_path_already_in_sys_path(self, monkeypatch):
        """Test when the path is already at the beginning of sys.path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, "w") as f:
                f.write("# test file")
            
            original_sys_path = sys.path.copy()
            
            try:
                # Set the path as first element in sys.path
                sys.path.insert(0, tmpdir)
                original_first_path = sys.path[0]
                
                result = prepare_import(test_file)
                assert result == "test"
                # Verify sys.path wasn't modified
                assert sys.path[0] == original_first_path
            finally:
                # Clean up sys.path
                sys.path[:] = original_sys_path
    
    def test_prepare_import_without_py_extension(self, monkeypatch):
        """Test path without .py extension"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test_module")
            with open(test_file, "w") as f:
                f.write("# test file")
            
            result = prepare_import(test_file)
            assert result == "test_module"
    
    def test_prepare_import_with_non_package_structure(self, monkeypatch):
        """Test file not in a package structure (no __init__.py)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "standalone.py")
            with open(test_file, "w") as f:
                f.write("# standalone file")
            
            original_sys_path = sys.path.copy()
            
            try:
                result = prepare_import(test_file)
                assert result == "standalone"
                # Verify tmpdir was added to sys.path
                assert tmpdir in sys.path
            finally:
                # Clean up sys.path
                sys.path[:] = original_sys_path
