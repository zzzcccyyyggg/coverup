# file: src/flask/src/flask/cli.py:636-655
# asked: {"lines": [636, 637, 639, 640, 644, 645, 646, 649, 650, 653, 655], "branches": []}
# gained: {"lines": [636, 637, 639, 640, 644, 645, 646, 649, 650, 653, 655], "branches": []}

import pytest
import click
from flask.cli import FlaskGroup, ScriptInfo, NoAppException
from unittest.mock import Mock, patch
import traceback

class TestFlaskGroupListCommands:
    
    def test_list_commands_no_app_exception(self, monkeypatch):
        """Test that NoAppException is caught and error message is printed."""
        # Create a mock context with ScriptInfo
        mock_ctx = Mock(spec=click.Context)
        mock_info = Mock(spec=ScriptInfo)
        mock_ctx.ensure_object.return_value = mock_info
        
        # Mock load_app to raise NoAppException
        mock_info.load_app.return_value.cli.list_commands.side_effect = NoAppException("Test app not found")
        
        # Create FlaskGroup instance
        group = FlaskGroup()
        
        # Mock _load_plugin_commands to do nothing
        monkeypatch.setattr(group, '_load_plugin_commands', lambda: None)
        
        # Mock super().list_commands to return some base commands
        with patch.object(FlaskGroup.__bases__[0], 'list_commands') as mock_super_list:
            mock_super_list.return_value = ['run', 'shell']
            
            # Mock click.secho to capture the error message
            with patch('click.secho') as mock_secho:
                result = group.list_commands(mock_ctx)
                
                # Verify the error message was printed with correct parameters
                mock_secho.assert_called_once()
                call_kwargs = mock_secho.call_args[1]
                assert call_kwargs['err'] == True
                assert call_kwargs['fg'] == "red"
                
                # Verify result contains only base commands (sorted)
                assert result == ['run', 'shell']
    
    def test_list_commands_generic_exception(self, monkeypatch):
        """Test that generic exceptions are caught and traceback is printed."""
        # Create a mock context with ScriptInfo
        mock_ctx = Mock(spec=click.Context)
        mock_info = Mock(spec=ScriptInfo)
        mock_ctx.ensure_object.return_value = mock_info
        
        # Mock load_app to raise a generic exception
        test_exception = RuntimeError("Something went wrong")
        mock_info.load_app.return_value.cli.list_commands.side_effect = test_exception
        
        # Create FlaskGroup instance
        group = FlaskGroup()
        
        # Mock _load_plugin_commands to do nothing
        monkeypatch.setattr(group, '_load_plugin_commands', lambda: None)
        
        # Mock super().list_commands to return some base commands
        with patch.object(FlaskGroup.__bases__[0], 'list_commands') as mock_super_list:
            mock_super_list.return_value = ['run', 'shell']
            
            # Mock click.secho to capture the traceback
            with patch('click.secho') as mock_secho:
                result = group.list_commands(mock_ctx)
                
                # Verify the traceback was printed with correct parameters
                mock_secho.assert_called_once()
                call_kwargs = mock_secho.call_args[1]
                assert call_kwargs['err'] == True
                assert call_kwargs['fg'] == "red"
                
                # Verify result contains only base commands (sorted)
                assert result == ['run', 'shell']
    
    def test_list_commands_successful_app_load(self, monkeypatch):
        """Test successful app load with additional commands."""
        # Create a mock context with ScriptInfo
        mock_ctx = Mock(spec=click.Context)
        mock_info = Mock(spec=ScriptInfo)
        mock_ctx.ensure_object.return_value = mock_info
        
        # Mock app and its CLI
        mock_app = Mock()
        mock_app.cli.list_commands.return_value = ['custom1', 'custom2']
        mock_info.load_app.return_value = mock_app
        
        # Create FlaskGroup instance
        group = FlaskGroup()
        
        # Mock _load_plugin_commands to do nothing
        monkeypatch.setattr(group, '_load_plugin_commands', lambda: None)
        
        # Mock super().list_commands to return base commands
        with patch.object(FlaskGroup.__bases__[0], 'list_commands') as mock_super_list:
            mock_super_list.return_value = ['run', 'shell']
            
            result = group.list_commands(mock_ctx)
            
            # Verify all commands are combined and sorted
            assert sorted(result) == ['custom1', 'custom2', 'run', 'shell']
