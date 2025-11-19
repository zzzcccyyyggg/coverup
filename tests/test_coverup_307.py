# file: src/flask/src/flask/cli.py:609-634
# asked: {"lines": [618, 622, 623, 624, 625, 626, 631, 632, 634], "branches": [[615, 618], [631, 632], [631, 634]]}
# gained: {"lines": [618, 622, 623, 624, 625, 626, 631, 632, 634], "branches": [[615, 618], [631, 632], [631, 634]]}

import pytest
import click
from flask import Flask
from flask.cli import FlaskGroup, ScriptInfo, NoAppException
from flask.globals import current_app


class TestFlaskGroupGetCommand:
    """Test cases for FlaskGroup.get_command method to cover lines 618-634."""
    
    def test_get_command_app_loads_successfully_no_current_app(self, monkeypatch):
        """Test when app loads successfully and no current app context exists."""
        # Create a mock app with a CLI that returns a command
        mock_command = click.Command('test_command')
        mock_app = Flask(__name__)
        mock_app.cli = click.Group()
        mock_app.cli.add_command(mock_command)
        
        # Create FlaskGroup instance
        group = FlaskGroup()
        
        # Create a mock context with ScriptInfo
        mock_ctx = click.Context(click.Command('test'))
        script_info = ScriptInfo()
        
        # Mock load_app to return our mock app
        def mock_load_app():
            return mock_app
        
        script_info.load_app = mock_load_app
        mock_ctx.obj = script_info
        
        # Mock ctx.with_resource to track if app context was pushed
        context_pushed = []
        original_with_resource = mock_ctx.with_resource
        
        def mock_with_resource(resource):
            context_pushed.append(resource)
            return original_with_resource(resource)
        
        monkeypatch.setattr(mock_ctx, 'with_resource', mock_with_resource)
        
        # Mock current_app check to simulate no current app
        monkeypatch.setattr('flask.cli.current_app', None)
        
        # Test that the command is found through app.cli
        result = group.get_command(mock_ctx, 'test_command')
        assert result is mock_command
        
        # Verify app context was pushed (ctx.with_resource was called with app_context)
        assert len(context_pushed) == 1
        assert hasattr(context_pushed[0], '__enter__')  # It's a context manager

    def test_get_command_app_loads_successfully_with_different_current_app(self, monkeypatch):
        """Test when app loads successfully but a different current app exists."""
        # Create two different mock apps
        existing_app = Flask('existing_app')
        mock_app = Flask('mock_app')
        mock_command = click.Command('test_command')
        mock_app.cli = click.Group()
        mock_app.cli.add_command(mock_command)
        
        # Create FlaskGroup instance
        group = FlaskGroup()
        
        # Create a mock context with ScriptInfo
        mock_ctx = click.Context(click.Command('test'))
        script_info = ScriptInfo()
        
        # Mock load_app to return our mock app
        def mock_load_app():
            return mock_app
        
        script_info.load_app = mock_load_app
        mock_ctx.obj = script_info
        
        # Mock ctx.with_resource to track if app context was pushed
        context_pushed = []
        original_with_resource = mock_ctx.with_resource
        
        def mock_with_resource(resource):
            context_pushed.append(resource)
            return original_with_resource(resource)
        
        monkeypatch.setattr(mock_ctx, 'with_resource', mock_with_resource)
        
        # Mock current_app and its _get_current_object to return existing_app
        class MockCurrentApp:
            def _get_current_object(self):
                return existing_app
        
        monkeypatch.setattr('flask.cli.current_app', MockCurrentApp())
        
        # Test that the command is found through app.cli
        result = group.get_command(mock_ctx, 'test_command')
        assert result is mock_command
        
        # Verify app context was pushed (ctx.with_resource was called with app_context)
        assert len(context_pushed) == 1
        assert hasattr(context_pushed[0], '__enter__')  # It's a context manager

    def test_get_command_app_load_fails_with_noappexception(self, monkeypatch):
        """Test when app loading fails with NoAppException."""
        # Create FlaskGroup instance
        group = FlaskGroup()
        
        # Create a mock context with ScriptInfo
        mock_ctx = click.Context(click.Command('test'))
        script_info = ScriptInfo()
        
        # Mock load_app to raise NoAppException
        def mock_load_app():
            raise NoAppException("No application found")
        
        script_info.load_app = mock_load_app
        mock_ctx.obj = script_info
        
        # Mock click.secho to capture the error message
        secho_calls = []
        def mock_secho(message, **kwargs):
            secho_calls.append((message, kwargs))
        
        monkeypatch.setattr(click, 'secho', mock_secho)
        
        # Test that None is returned when app loading fails
        result = group.get_command(mock_ctx, 'nonexistent_command')
        assert result is None
        
        # Verify error message was printed
        assert len(secho_calls) == 1
        message, kwargs = secho_calls[0]
        assert "Error: No application found" in message
        assert kwargs.get('err') is True
        assert kwargs.get('fg') == 'red'

    def test_get_command_app_loads_successfully_same_current_app(self, monkeypatch):
        """Test when app loads successfully and same app is already current."""
        # Create a mock app
        mock_app = Flask(__name__)
        mock_command = click.Command('test_command')
        mock_app.cli = click.Group()
        mock_app.cli.add_command(mock_command)
        
        # Create FlaskGroup instance
        group = FlaskGroup()
        
        # Create a mock context with ScriptInfo
        mock_ctx = click.Context(click.Command('test'))
        script_info = ScriptInfo()
        
        # Mock load_app to return our mock app
        def mock_load_app():
            return mock_app
        
        script_info.load_app = mock_load_app
        mock_ctx.obj = script_info
        
        # Mock ctx.with_resource to track if app context was pushed
        context_pushed = []
        original_with_resource = mock_ctx.with_resource
        
        def mock_with_resource(resource):
            context_pushed.append(resource)
            return original_with_resource(resource)
        
        monkeypatch.setattr(mock_ctx, 'with_resource', mock_with_resource)
        
        # Mock current_app and its _get_current_object to return mock_app
        class MockCurrentApp:
            def _get_current_object(self):
                return mock_app
        
        monkeypatch.setattr('flask.cli.current_app', MockCurrentApp())
        
        # Test that the command is found through app.cli
        result = group.get_command(mock_ctx, 'test_command')
        assert result is mock_command
        
        # Verify app context was NOT pushed (same app is already current)
        assert len(context_pushed) == 0
