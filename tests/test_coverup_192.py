# file: src/flask/src/flask/cli.py:678-688
# asked: {"lines": [678, 679, 680, 685, 686, 688], "branches": [[679, 685], [679, 688]]}
# gained: {"lines": [678, 679, 680, 685, 686, 688], "branches": [[679, 685], [679, 688]]}

import pytest
import click
from flask.cli import FlaskGroup, _env_file_option, _app_option


class TestFlaskGroupParseArgs:
    """Test cases for FlaskGroup.parse_args method to achieve full coverage."""
    
    def test_parse_args_no_args_is_help(self, monkeypatch):
        """Test parse_args when no args are provided and no_args_is_help is True."""
        # Create a FlaskGroup with no_args_is_help=True
        group = FlaskGroup()
        group.no_args_is_help = True
        
        # Mock the handle_parse_result methods to track if they were called
        env_file_called = False
        app_option_called = False
        
        def mock_env_file_handle(ctx, opts, args):
            nonlocal env_file_called
            env_file_called = True
        
        def mock_app_option_handle(ctx, opts, args):
            nonlocal app_option_called
            app_option_called = True
        
        monkeypatch.setattr(_env_file_option, 'handle_parse_result', mock_env_file_handle)
        monkeypatch.setattr(_app_option, 'handle_parse_result', mock_app_option_handle)
        
        # Mock the parent class parse_args method
        def mock_parse_args(self, ctx, args):
            return []
        
        monkeypatch.setattr(click.Group, 'parse_args', mock_parse_args)
        
        # Create a mock context
        ctx = click.Context(click.Command('test'))
        
        # Call parse_args with no args
        result = group.parse_args(ctx, [])
        
        # Verify that env_file and app_option handlers were called
        assert env_file_called
        assert app_option_called
        assert result == []
    
    def test_parse_args_single_help_option(self, monkeypatch):
        """Test parse_args when single help option is provided."""
        group = FlaskGroup()
        
        # Mock the handle_parse_result methods to track if they were called
        env_file_called = False
        app_option_called = False
        
        def mock_env_file_handle(ctx, opts, args):
            nonlocal env_file_called
            env_file_called = True
        
        def mock_app_option_handle(ctx, opts, args):
            nonlocal app_option_called
            app_option_called = True
        
        monkeypatch.setattr(_env_file_option, 'handle_parse_result', mock_env_file_handle)
        monkeypatch.setattr(_app_option, 'handle_parse_result', mock_app_option_handle)
        
        # Mock the parent class parse_args method
        def mock_parse_args(self, ctx, args):
            return ['--help']
        
        monkeypatch.setattr(click.Group, 'parse_args', mock_parse_args)
        
        # Create a mock context
        ctx = click.Context(click.Command('test'))
        
        # Mock get_help_option_names to return ['--help', '-h']
        def mock_get_help_option_names(ctx):
            return ['--help', '-h']
        
        monkeypatch.setattr(group, 'get_help_option_names', mock_get_help_option_names)
        
        # Call parse_args with help option
        result = group.parse_args(ctx, ['--help'])
        
        # Verify that env_file and app_option handlers were called
        assert env_file_called
        assert app_option_called
        assert result == ['--help']
    
    def test_parse_args_normal_case(self, monkeypatch):
        """Test parse_args in normal case (not help scenario)."""
        group = FlaskGroup()
        
        # Mock the handle_parse_result methods to track if they were called
        env_file_called = False
        app_option_called = False
        
        def mock_env_file_handle(ctx, opts, args):
            nonlocal env_file_called
            env_file_called = True
        
        def mock_app_option_handle(ctx, opts, args):
            nonlocal app_option_called
            app_option_called = True
        
        monkeypatch.setattr(_env_file_option, 'handle_parse_result', mock_env_file_handle)
        monkeypatch.setattr(_app_option, 'handle_parse_result', mock_app_option_handle)
        
        # Mock the parent class parse_args method
        def mock_parse_args(self, ctx, args):
            return args
        
        monkeypatch.setattr(click.Group, 'parse_args', mock_parse_args)
        
        # Create a mock context
        ctx = click.Context(click.Command('test'))
        
        # Call parse_args with multiple args (not help scenario)
        args = ['run', '--host', 'localhost']
        result = group.parse_args(ctx, args)
        
        # Verify that env_file and app_option handlers were NOT called
        assert not env_file_called
        assert not app_option_called
        assert result == args
