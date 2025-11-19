# file: src/flask/src/flask/cli.py:333-372
# asked: {"lines": [333, 338, 339, 340, 341, 342, 344, 345, 346, 347, 348, 349, 351, 352, 353, 355, 356, 358, 359, 360, 366, 369, 371, 372], "branches": [[338, 339], [338, 340], [341, 342], [341, 344], [344, 345], [344, 351], [351, 352], [351, 358], [355, 351], [355, 356], [358, 359], [358, 366], [366, 369], [366, 371]]}
# gained: {"lines": [333, 338, 339, 340, 341, 342, 344, 345, 346, 347, 348, 349, 351, 352, 353, 355, 356, 358, 359, 360, 366, 369, 371, 372], "branches": [[338, 339], [338, 340], [341, 342], [341, 344], [344, 345], [344, 351], [351, 352], [351, 358], [355, 351], [355, 356], [358, 359], [358, 366], [366, 369], [366, 371]]}

import pytest
import re
import sys
import os
from unittest.mock import Mock, patch
from flask.cli import ScriptInfo, NoAppException, prepare_import, locate_app
from flask.helpers import get_debug_flag
from flask.app import Flask


class TestScriptInfoLoadApp:
    """Test cases for ScriptInfo.load_app method to achieve full coverage."""
    
    def test_load_app_with_loaded_app(self):
        """Test that load_app returns already loaded app without reloading."""
        script_info = ScriptInfo()
        mock_app = Mock(spec=Flask)
        script_info._loaded_app = mock_app
        
        result = script_info.load_app()
        
        assert result is mock_app
    
    def test_load_app_with_create_app(self):
        """Test load_app when create_app is provided."""
        mock_app = Mock(spec=Flask)
        script_info = ScriptInfo(create_app=lambda: mock_app)
        
        result = script_info.load_app()
        
        assert result is mock_app
        assert script_info._loaded_app is mock_app
    
    def test_load_app_with_app_import_path(self):
        """Test load_app with app_import_path provided."""
        with patch('flask.cli.prepare_import') as mock_prepare, \
             patch('flask.cli.locate_app') as mock_locate:
            mock_prepare.return_value = 'test_module'
            mock_app = Mock(spec=Flask)
            mock_locate.return_value = mock_app
            
            script_info = ScriptInfo(app_import_path='myapp:app')
            result = script_info.load_app()
            
            mock_prepare.assert_called_once_with('myapp')
            mock_locate.assert_called_once_with('test_module', 'app')
            assert result is mock_app
            assert script_info._loaded_app is mock_app
    
    def test_load_app_with_app_import_path_no_name(self):
        """Test load_app with app_import_path but no app name."""
        with patch('flask.cli.prepare_import') as mock_prepare, \
             patch('flask.cli.locate_app') as mock_locate:
            mock_prepare.return_value = 'test_module'
            mock_app = Mock(spec=Flask)
            mock_locate.return_value = mock_app
            
            script_info = ScriptInfo(app_import_path='myapp')
            result = script_info.load_app()
            
            mock_prepare.assert_called_once_with('myapp')
            mock_locate.assert_called_once_with('test_module', None)
            assert result is mock_app
            assert script_info._loaded_app is mock_app
    
    def test_load_app_finds_wsgi_py(self):
        """Test load_app finds app in wsgi.py."""
        with patch('flask.cli.prepare_import') as mock_prepare, \
             patch('flask.cli.locate_app') as mock_locate:
            mock_prepare.side_effect = ['wsgi_module', 'app_module']
            mock_app = Mock(spec=Flask)
            mock_locate.side_effect = [None, mock_app]
            
            script_info = ScriptInfo()
            result = script_info.load_app()
            
            assert mock_prepare.call_count == 2
            mock_prepare.assert_any_call('wsgi.py')
            mock_prepare.assert_any_call('app.py')
            assert mock_locate.call_count == 2
            mock_locate.assert_any_call('wsgi_module', None, raise_if_not_found=False)
            mock_locate.assert_any_call('app_module', None, raise_if_not_found=False)
            assert result is mock_app
            assert script_info._loaded_app is mock_app
    
    def test_load_app_finds_app_py(self):
        """Test load_app finds app in app.py."""
        with patch('flask.cli.prepare_import') as mock_prepare, \
             patch('flask.cli.locate_app') as mock_locate:
            mock_prepare.return_value = 'app_module'
            mock_app = Mock(spec=Flask)
            mock_locate.return_value = mock_app
            
            script_info = ScriptInfo()
            result = script_info.load_app()
            
            mock_prepare.assert_called_once_with('wsgi.py')
            mock_locate.assert_called_once_with('app_module', None, raise_if_not_found=False)
            assert result is mock_app
            assert script_info._loaded_app is mock_app
    
    def test_load_app_no_app_found_raises_exception(self):
        """Test load_app raises NoAppException when no app can be found."""
        with patch('flask.cli.prepare_import') as mock_prepare, \
             patch('flask.cli.locate_app') as mock_locate:
            mock_prepare.side_effect = ['wsgi_module', 'app_module']
            mock_locate.return_value = None
            
            script_info = ScriptInfo()
            
            with pytest.raises(NoAppException) as exc_info:
                script_info.load_app()
            
            assert "Could not locate a Flask application" in str(exc_info.value)
    
    def test_load_app_sets_debug_flag(self):
        """Test load_app sets debug flag when set_debug_flag is True."""
        with patch('flask.cli.get_debug_flag') as mock_get_debug:
            mock_get_debug.return_value = True
            mock_app = Mock(spec=Flask)
            script_info = ScriptInfo(create_app=lambda: mock_app, set_debug_flag=True)
            
            result = script_info.load_app()
            
            mock_get_debug.assert_called_once()
            assert mock_app.debug is True
            assert result is mock_app
    
    def test_load_app_does_not_set_debug_flag(self):
        """Test load_app does not set debug flag when set_debug_flag is False."""
        with patch('flask.cli.get_debug_flag') as mock_get_debug:
            mock_app = Mock(spec=Flask)
            script_info = ScriptInfo(create_app=lambda: mock_app, set_debug_flag=False)
            
            result = script_info.load_app()
            
            mock_get_debug.assert_not_called()
            assert result is mock_app
    
    def test_load_app_app_import_path_with_colon_in_path(self):
        """Test load_app with app_import_path containing colon in Windows path."""
        with patch('flask.cli.prepare_import') as mock_prepare, \
             patch('flask.cli.locate_app') as mock_locate:
            mock_prepare.return_value = 'test_module'
            mock_app = Mock(spec=Flask)
            mock_locate.return_value = mock_app
            
            # Test with Windows-style path containing colon (C:\path\to\app)
            script_info = ScriptInfo(app_import_path='C:\\path\\to\\app:myapp')
            result = script_info.load_app()
            
            # Should split on colon not followed by backslash or forward slash
            mock_prepare.assert_called_once_with('C:\\path\\to\\app')
            mock_locate.assert_called_once_with('test_module', 'myapp')
            assert result is mock_app
