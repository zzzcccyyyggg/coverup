# file: src/click/src/click/utils.py:449-495
# asked: {"lines": [449, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 492, 493, 494], "branches": [[480, 481], [480, 486], [483, 484], [483, 485], [486, 487], [486, 488], [488, 489], [488, 492]]}
# gained: {"lines": [449, 480, 486, 487, 488, 489, 490, 492, 493, 494], "branches": [[480, 486], [486, 487], [486, 488], [488, 489], [488, 492]]}

import os
import sys
import pytest
from click.utils import get_app_dir, _posixify
from click._compat import WIN


class TestGetAppDir:
    """Test cases for get_app_dir function to achieve full coverage."""
    
    def test_windows_roaming_appdata_set(self, monkeypatch):
        """Test Windows roaming path when APPDATA is set."""
        if not WIN:
            pytest.skip("Test only runs on Windows")
        
        monkeypatch.setattr('click._compat.WIN', True)
        monkeypatch.setenv('APPDATA', r'C:\Users\test\AppData\Roaming')
        monkeypatch.delenv('LOCALAPPDATA', raising=False)
        
        result = get_app_dir('My App', roaming=True)
        expected = os.path.join(r'C:\Users\test\AppData\Roaming', 'My App')
        assert result == expected
    
    def test_windows_roaming_appdata_not_set(self, monkeypatch):
        """Test Windows roaming path when APPDATA is not set."""
        if not WIN:
            pytest.skip("Test only runs on Windows")
        
        monkeypatch.setattr('click._compat.WIN', True)
        monkeypatch.delenv('APPDATA', raising=False)
        monkeypatch.delenv('LOCALAPPDATA', raising=False)
        
        result = get_app_dir('My App', roaming=True)
        expected = os.path.join(os.path.expanduser("~"), 'My App')
        assert result == expected
    
    def test_windows_local_appdata_set(self, monkeypatch):
        """Test Windows local path when LOCALAPPDATA is set."""
        if not WIN:
            pytest.skip("Test only runs on Windows")
        
        monkeypatch.setattr('click._compat.WIN', True)
        monkeypatch.delenv('APPDATA', raising=False)
        monkeypatch.setenv('LOCALAPPDATA', r'C:\Users\test\AppData\Local')
        
        result = get_app_dir('My App', roaming=False)
        expected = os.path.join(r'C:\Users\test\AppData\Local', 'My App')
        assert result == expected
    
    def test_windows_local_appdata_not_set(self, monkeypatch):
        """Test Windows local path when LOCALAPPDATA is not set."""
        if not WIN:
            pytest.skip("Test only runs on Windows")
        
        monkeypatch.setattr('click._compat.WIN', True)
        monkeypatch.delenv('APPDATA', raising=False)
        monkeypatch.delenv('LOCALAPPDATA', raising=False)
        
        result = get_app_dir('My App', roaming=False)
        expected = os.path.join(os.path.expanduser("~"), 'My App')
        assert result == expected
    
    def test_force_posix(self, monkeypatch):
        """Test force_posix=True on non-Windows systems."""
        monkeypatch.setattr('click._compat.WIN', False)
        
        result = get_app_dir('My App', force_posix=True)
        expected = os.path.join(os.path.expanduser("~"), '.my-app')
        assert result == expected
    
    def test_darwin_platform(self, monkeypatch):
        """Test macOS platform path."""
        monkeypatch.setattr('click._compat.WIN', False)
        monkeypatch.setattr('sys.platform', 'darwin')
        
        result = get_app_dir('My App')
        expected = os.path.join(os.path.expanduser("~/Library/Application Support"), 'My App')
        assert result == expected
    
    def test_unix_with_xdg_config_home(self, monkeypatch):
        """Test Unix platform with XDG_CONFIG_HOME set."""
        monkeypatch.setattr('click._compat.WIN', False)
        monkeypatch.setattr('sys.platform', 'linux')
        monkeypatch.setenv('XDG_CONFIG_HOME', '/custom/config')
        
        result = get_app_dir('My App')
        expected = os.path.join('/custom/config', 'my-app')
        assert result == expected
    
    def test_unix_without_xdg_config_home(self, monkeypatch):
        """Test Unix platform without XDG_CONFIG_HOME set."""
        monkeypatch.setattr('click._compat.WIN', False)
        monkeypatch.setattr('sys.platform', 'linux')
        monkeypatch.delenv('XDG_CONFIG_HOME', raising=False)
        
        result = get_app_dir('My App')
        expected = os.path.join(os.path.expanduser("~/.config"), 'my-app')
        assert result == expected
