# file: src/flask/src/flask/sansio/scaffold.py:754-792
# asked: {"lines": [754, 767, 768, 771, 772, 774, 777, 778, 781, 782, 785, 786, 789, 792], "branches": [[771, 772], [771, 774], [777, 778], [777, 792], [781, 782], [781, 785], [785, 786], [785, 789]]}
# gained: {"lines": [754, 767, 768, 771, 772, 774, 777, 778, 781, 782, 785, 786, 789, 792], "branches": [[771, 772], [771, 774], [777, 778], [777, 792], [781, 782], [781, 785], [785, 786], [785, 789]]}

import os
import pathlib
import sys
import pytest
from unittest.mock import patch, MagicMock
import tempfile
import importlib.util

def test_find_package_installed_to_system():
    """Test when package is installed to system prefix"""
    import_name = "test_package"
    mock_package_path = os.path.join(sys.prefix, "lib", "python3.8", "site-packages", "test_package")
    
    with patch('flask.sansio.scaffold._find_package_path') as mock_find:
        mock_find.return_value = mock_package_path
        from flask.sansio.scaffold import find_package
        
        prefix, path = find_package(import_name)
        
        assert prefix == os.path.abspath(sys.prefix)
        assert path == mock_package_path

def test_find_package_installed_to_virtualenv_windows():
    """Test when package is installed to virtualenv on Windows"""
    import_name = "test_package"
    mock_package_path = os.path.join("C:", "virtualenv", "lib", "site-packages", "test_package")
    
    with patch('flask.sansio.scaffold._find_package_path') as mock_find:
        mock_find.return_value = mock_package_path
        with patch('pathlib.PurePath.is_relative_to') as mock_relative:
            mock_relative.return_value = False
            with patch('os.path.split') as mock_split:
                mock_split.side_effect = [
                    ("C:\\virtualenv\\lib", "site-packages"),
                    ("C:\\virtualenv", "lib")
                ]
                from flask.sansio.scaffold import find_package
                
                prefix, path = find_package(import_name)
                
                assert prefix == "C:\\virtualenv"
                assert path == mock_package_path

def test_find_package_installed_to_virtualenv_unix():
    """Test when package is installed to virtualenv on Unix"""
    import_name = "test_package"
    mock_package_path = os.path.join("/virtualenv", "lib", "python3.8", "site-packages", "test_package")
    
    with patch('flask.sansio.scaffold._find_package_path') as mock_find:
        mock_find.return_value = mock_package_path
        with patch('pathlib.PurePath.is_relative_to') as mock_relative:
            mock_relative.return_value = False
            with patch('os.path.split') as mock_split:
                mock_split.side_effect = [
                    ("/virtualenv/lib/python3.8", "site-packages"),
                    ("/virtualenv/lib", "python3.8")
                ]
                with patch('os.path.basename') as mock_basename:
                    mock_basename.return_value = "lib"
                    from flask.sansio.scaffold import find_package
                    
                    prefix, path = find_package(import_name)
                    
                    assert prefix == "/virtualenv"
                    assert path == mock_package_path

def test_find_package_installed_to_virtualenv_other():
    """Test when package is installed to virtualenv with non-standard structure"""
    import_name = "test_package"
    mock_package_path = os.path.join("/virtualenv", "site-packages", "test_package")
    
    with patch('flask.sansio.scaffold._find_package_path') as mock_find:
        mock_find.return_value = mock_package_path
        with patch('pathlib.PurePath.is_relative_to') as mock_relative:
            mock_relative.return_value = False
            with patch('os.path.split') as mock_split:
                mock_split.side_effect = [
                    ("/virtualenv", "site-packages"),
                    ("/virtualenv", "site-packages")
                ]
                from flask.sansio.scaffold import find_package
                
                prefix, path = find_package(import_name)
                
                assert prefix == "/virtualenv"
                assert path == mock_package_path

def test_find_package_not_installed():
    """Test when package is not installed (returns None for prefix)"""
    import_name = "test_package"
    mock_package_path = os.path.join("/some", "custom", "path", "test_package")
    
    with patch('flask.sansio.scaffold._find_package_path') as mock_find:
        mock_find.return_value = mock_package_path
        with patch('pathlib.PurePath.is_relative_to') as mock_relative:
            mock_relative.return_value = False
            with patch('os.path.split') as mock_split:
                mock_split.side_effect = [
                    ("/some/custom/path", "test_package"),
                    ("/some/custom", "path")
                ]
                from flask.sansio.scaffold import find_package
                
                prefix, path = find_package(import_name)
                
                assert prefix is None
                assert path == mock_package_path
