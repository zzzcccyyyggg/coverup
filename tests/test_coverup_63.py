# file: src/flask/src/flask/cli.py:766-777
# asked: {"lines": [766, 770, 771, 773, 774, 776, 777], "branches": [[770, 771], [770, 773], [773, 774], [773, 776], [776, 0], [776, 777]]}
# gained: {"lines": [766, 770, 771, 773, 774, 776, 777], "branches": [[770, 771], [770, 773], [773, 774], [773, 776], [776, 0], [776, 777]]}

import pytest
from unittest.mock import patch, MagicMock
from flask.cli import show_server_banner


class TestShowServerBanner:
    """Test cases for show_server_banner function to achieve full coverage."""
    
    def test_show_server_banner_with_reloader(self, monkeypatch):
        """Test that function returns early when running from reloader."""
        monkeypatch.setattr('flask.cli.is_running_from_reloader', lambda: True)
        
        with patch('flask.cli.click.echo') as mock_echo:
            show_server_banner(debug=True, app_import_path="test_app")
            
            # No echo calls should be made when running from reloader
            mock_echo.assert_not_called()
    
    def test_show_server_banner_with_app_path_and_debug_on(self, monkeypatch):
        """Test banner with app path and debug mode on."""
        monkeypatch.setattr('flask.cli.is_running_from_reloader', lambda: False)
        
        with patch('flask.cli.click.echo') as mock_echo:
            show_server_banner(debug=True, app_import_path="my_app")
            
            # Verify both messages are printed
            assert mock_echo.call_count == 2
            mock_echo.assert_any_call(" * Serving Flask app 'my_app'")
            mock_echo.assert_any_call(" * Debug mode: on")
    
    def test_show_server_banner_with_app_path_and_debug_off(self, monkeypatch):
        """Test banner with app path and debug mode off."""
        monkeypatch.setattr('flask.cli.is_running_from_reloader', lambda: False)
        
        with patch('flask.cli.click.echo') as mock_echo:
            show_server_banner(debug=False, app_import_path="my_app")
            
            # Verify both messages are printed
            assert mock_echo.call_count == 2
            mock_echo.assert_any_call(" * Serving Flask app 'my_app'")
            mock_echo.assert_any_call(" * Debug mode: off")
    
    def test_show_server_banner_with_app_path_only(self, monkeypatch):
        """Test banner with app path but no debug mode specified."""
        monkeypatch.setattr('flask.cli.is_running_from_reloader', lambda: False)
        
        with patch('flask.cli.click.echo') as mock_echo:
            show_server_banner(debug=None, app_import_path="my_app")
            
            # Verify only app path message is printed
            assert mock_echo.call_count == 1
            mock_echo.assert_called_once_with(" * Serving Flask app 'my_app'")
    
    def test_show_server_banner_with_debug_only(self, monkeypatch):
        """Test banner with debug mode but no app path."""
        monkeypatch.setattr('flask.cli.is_running_from_reloader', lambda: False)
        
        with patch('flask.cli.click.echo') as mock_echo:
            show_server_banner(debug=True, app_import_path=None)
            
            # Verify only debug message is printed
            assert mock_echo.call_count == 1
            mock_echo.assert_called_once_with(" * Debug mode: on")
    
    def test_show_server_banner_with_debug_off_only(self, monkeypatch):
        """Test banner with debug mode off but no app path."""
        monkeypatch.setattr('flask.cli.is_running_from_reloader', lambda: False)
        
        with patch('flask.cli.click.echo') as mock_echo:
            show_server_banner(debug=False, app_import_path=None)
            
            # Verify only debug message is printed
            assert mock_echo.call_count == 1
            mock_echo.assert_called_once_with(" * Debug mode: off")
    
    def test_show_server_banner_no_app_path_no_debug(self, monkeypatch):
        """Test banner with no app path and no debug mode specified."""
        monkeypatch.setattr('flask.cli.is_running_from_reloader', lambda: False)
        
        with patch('flask.cli.click.echo') as mock_echo:
            show_server_banner(debug=None, app_import_path=None)
            
            # No messages should be printed
            mock_echo.assert_not_called()
