# file: src/flask/src/flask/sansio/scaffold.py:709-751
# asked: {"lines": [709, 711, 713, 714, 716, 717, 718, 724, 726, 727, 729, 731, 733, 734, 736, 737, 738, 739, 743, 745, 748, 751], "branches": [[716, 717], [716, 726], [726, 727], [726, 751], [727, 729], [727, 748], [731, 733], [731, 743]]}
# gained: {"lines": [709, 711, 713, 714, 716, 717, 718, 724, 726, 727, 729, 731, 733, 734, 736, 737, 738, 739, 743, 745, 748, 751], "branches": [[716, 717], [716, 726], [726, 727], [726, 751], [727, 729], [727, 748], [731, 733], [731, 743]]}

import pytest
import importlib.util
import os
import pathlib
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Import the function directly from the module
from flask.sansio.scaffold import _find_package_path

def test_find_package_path_import_error():
    """Test _find_package_path when ImportError occurs."""
    with patch('importlib.util.find_spec', side_effect=ImportError):
        result = _find_package_path('nonexistent_module')
        assert result == os.getcwd()

def test_find_package_path_value_error_none_spec():
    """Test _find_package_path when root_spec is None (raises ValueError)."""
    with patch('importlib.util.find_spec', return_value=None):
        result = _find_package_path('nonexistent_module')
        assert result == os.getcwd()

def test_find_package_path_namespace_package_with_submodule():
    """Test _find_package_path for namespace package with submodule."""
    mock_root_spec = MagicMock()
    mock_root_spec.submodule_search_locations = ['/path/to/namespace1', '/path/to/namespace2']
    mock_root_spec.origin = 'namespace'
    
    mock_package_spec = MagicMock()
    mock_package_spec.submodule_search_locations = ['/path/to/namespace1/submodule']
    
    with patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.side_effect = [mock_root_spec, mock_package_spec]
        
        with patch('pathlib.Path.is_relative_to', return_value=True):
            result = _find_package_path('namespace_pkg.submodule')
            assert result == os.path.dirname('/path/to/namespace1')

def test_find_package_path_namespace_package_no_submodule():
    """Test _find_package_path for namespace package without submodule."""
    mock_root_spec = MagicMock()
    mock_root_spec.submodule_search_locations = ['/path/to/namespace1', '/path/to/namespace2']
    mock_root_spec.origin = 'namespace'
    
    mock_package_spec = MagicMock()
    mock_package_spec.submodule_search_locations = None
    
    with patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.side_effect = [mock_root_spec, mock_package_spec]
        
        result = _find_package_path('namespace_pkg.submodule')
        assert result == os.path.dirname('/path/to/namespace1')

def test_find_package_path_regular_package():
    """Test _find_package_path for regular package with __init__.py."""
    mock_root_spec = MagicMock()
    mock_root_spec.submodule_search_locations = ['/path/to/package']
    mock_root_spec.origin = '/path/to/package/__init__.py'
    
    with patch('importlib.util.find_spec', return_value=mock_root_spec):
        result = _find_package_path('regular_package')
        assert result == os.path.dirname('/path/to/package')

def test_find_package_path_module():
    """Test _find_package_path for regular module."""
    mock_root_spec = MagicMock()
    mock_root_spec.submodule_search_locations = None
    mock_root_spec.origin = '/path/to/module.py'
    
    with patch('importlib.util.find_spec', return_value=mock_root_spec):
        result = _find_package_path('module')
        assert result == os.path.dirname('/path/to/module.py')
