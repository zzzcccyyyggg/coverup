# file: src/flask/src/flask/cli.py:600-607
# asked: {"lines": [600, 601, 602, 604, 605, 607], "branches": [[601, 602], [601, 604], [604, 605], [604, 607]]}
# gained: {"lines": [600, 601, 602, 604, 605, 607], "branches": [[601, 602], [601, 604], [604, 605], [604, 607]]}

import pytest
import importlib.metadata
from unittest.mock import Mock, patch
from flask.cli import FlaskGroup


class TestFlaskGroupLoadPluginCommands:
    """Test cases for FlaskGroup._load_plugin_commands method."""
    
    def test_load_plugin_commands_already_loaded(self):
        """Test that _load_plugin_commands returns early if already loaded."""
        group = FlaskGroup()
        group._loaded_plugin_commands = True
        
        # Mock entry_points to ensure it's not called if already loaded
        with patch('importlib.metadata.entry_points') as mock_entry_points:
            group._load_plugin_commands()
            
            # Verify entry_points was not called since we returned early
            mock_entry_points.assert_not_called()
    
    def test_load_plugin_commands_with_plugins(self):
        """Test _load_plugin_commands loads plugins from entry points."""
        group = FlaskGroup()
        group._loaded_plugin_commands = False
        
        # Create mock entry points
        mock_command1 = Mock()
        mock_command2 = Mock()
        
        mock_ep1 = Mock()
        mock_ep1.name = "test_command1"
        mock_ep1.load.return_value = mock_command1
        
        mock_ep2 = Mock()
        mock_ep2.name = "test_command2" 
        mock_ep2.load.return_value = mock_command2
        
        mock_entry_points = Mock()
        mock_entry_points.return_value = [mock_ep1, mock_ep2]
        
        with patch('importlib.metadata.entry_points', mock_entry_points):
            with patch.object(group, 'add_command') as mock_add_command:
                group._load_plugin_commands()
                
                # Verify entry_points was called with correct group
                mock_entry_points.assert_called_once_with(group="flask.commands")
                
                # Verify add_command was called for each entry point
                assert mock_add_command.call_count == 2
                mock_add_command.assert_any_call(mock_command1, "test_command1")
                mock_add_command.assert_any_call(mock_command2, "test_command2")
                
                # Verify _loaded_plugin_commands is now True
                assert group._loaded_plugin_commands is True
    
    def test_load_plugin_commands_no_plugins(self):
        """Test _load_plugin_commands when no plugins are found."""
        group = FlaskGroup()
        group._loaded_plugin_commands = False
        
        # Mock empty entry points
        mock_entry_points = Mock()
        mock_entry_points.return_value = []
        
        with patch('importlib.metadata.entry_points', mock_entry_points):
            with patch.object(group, 'add_command') as mock_add_command:
                group._load_plugin_commands()
                
                # Verify entry_points was called with correct group
                mock_entry_points.assert_called_once_with(group="flask.commands")
                
                # Verify add_command was not called since no plugins
                mock_add_command.assert_not_called()
                
                # Verify _loaded_plugin_commands is now True
                assert group._loaded_plugin_commands is True
