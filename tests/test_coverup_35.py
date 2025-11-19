# file: src/flask/src/flask/helpers.py:571-625
# asked: {"lines": [571, 581, 583, 584, 587, 588, 590, 591, 592, 593, 595, 600, 601, 603, 604, 607, 608, 609, 614, 615, 616, 617, 625], "branches": [[583, 584], [583, 587], [590, 591], [590, 595], [600, 601], [600, 603], [603, 604], [603, 607], [614, 615], [614, 625]]}
# gained: {"lines": [571, 581, 583, 587, 588, 590, 591, 592, 593, 595, 600, 601, 603, 604, 607, 608, 609, 614, 615, 616, 617, 625], "branches": [[583, 587], [590, 591], [590, 595], [600, 601], [600, 603], [603, 604], [603, 607], [614, 615], [614, 625]]}

import pytest
import sys
import os
import importlib.util
import types
from unittest.mock import Mock, patch


class TestGetRootPath:
    """Test cases for get_root_path function to achieve full coverage."""
    
    def test_get_root_path_with_nonexistent_module(self, monkeypatch):
        """Test when module doesn't exist and spec is None (lines 590-593)."""
        from flask.helpers import get_root_path
        
        # Mock find_spec to return None
        def mock_find_spec(name):
            return None
            
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)
        
        # Should return current working directory
        result = get_root_path('nonexistent_module_12345')
        assert result == os.getcwd()
    
    def test_get_root_path_with_loader_without_get_filename(self, monkeypatch):
        """Test when loader exists but doesn't have get_filename (lines 603, 607-609)."""
        from flask.helpers import get_root_path
        
        # Create a mock loader without get_filename
        mock_loader = Mock(spec=[])
        
        # Create a mock spec with the loader
        mock_spec = Mock()
        mock_spec.loader = mock_loader
        
        # Mock find_spec to return our spec
        def mock_find_spec(name):
            return mock_spec
            
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)
        
        # Create a mock module that will be imported
        mock_module = types.ModuleType('test_module')
        mock_module.__file__ = '/some/path/test_module.py'
        
        # Mock __import__ to return our mock module
        def mock_import(name, *args, **kwargs):
            sys.modules[name] = mock_module
            return mock_module
            
        monkeypatch.setattr('builtins.__import__', mock_import)
        
        result = get_root_path('test_module')
        assert result == os.path.dirname(os.path.abspath('/some/path/test_module.py'))
        
        # Clean up
        if 'test_module' in sys.modules:
            del sys.modules['test_module']
    
    def test_get_root_path_with_namespace_package_error(self, monkeypatch):
        """Test when filepath is None (namespace package case, lines 614-617)."""
        from flask.helpers import get_root_path
        
        # Create a mock loader without get_filename
        mock_loader = Mock(spec=[])
        
        # Create a mock spec with the loader
        mock_spec = Mock()
        mock_spec.loader = mock_loader
        
        # Mock find_spec to return our spec
        def mock_find_spec(name):
            return mock_spec
            
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)
        
        # Create a mock module with no __file__ (namespace package)
        mock_module = types.ModuleType('namespace_module')
        mock_module.__file__ = None
        
        # Mock __import__ to return our mock module
        def mock_import(name, *args, **kwargs):
            sys.modules[name] = mock_module
            return mock_module
            
        monkeypatch.setattr('builtins.__import__', mock_import)
        
        # Should raise RuntimeError for namespace package
        with pytest.raises(RuntimeError) as exc_info:
            get_root_path('namespace_module')
        
        assert "No root path can be found for the provided module" in str(exc_info.value)
        assert "namespace_module" in str(exc_info.value)
        
        # Clean up
        if 'namespace_module' in sys.modules:
            del sys.modules['namespace_module']
    
    def test_get_root_path_with_loader_having_get_filename(self, monkeypatch):
        """Test when loader has get_filename method (lines 603-604)."""
        from flask.helpers import get_root_path
        
        # Create a mock loader with get_filename
        mock_loader = Mock()
        mock_loader.get_filename.return_value = '/some/path/module.py'
        
        # Create a mock spec with the loader
        mock_spec = Mock()
        mock_spec.loader = mock_loader
        
        # Mock find_spec to return our spec
        def mock_find_spec(name):
            return mock_spec
            
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)
        
        result = get_root_path('some_module')
        assert result == os.path.dirname(os.path.abspath('/some/path/module.py'))
        mock_loader.get_filename.assert_called_once_with('some_module')
