# file: src/click/src/click/exceptions.py:268-274
# asked: {"lines": [268, 269, 270, 271, 273, 274], "branches": []}
# gained: {"lines": [268, 269, 270, 271, 273, 274], "branches": []}

import pytest
import io
from click.exceptions import NoArgsIsHelpError
from click.core import Context
from click import Command

class TestNoArgsIsHelpError:
    def test_no_args_is_help_error_initialization(self):
        """Test that NoArgsIsHelpError initializes correctly with a context."""
        ctx = Context(Command('test_cmd'))
        error = NoArgsIsHelpError(ctx)
        
        assert error.ctx == ctx
        assert error.message == ctx.get_help()
        assert error.exit_code == 2  # Inherited from UsageError

    def test_no_args_is_help_error_show_method(self, monkeypatch):
        """Test that the show method calls echo with correct parameters."""
        ctx = Context(Command('test_cmd'))
        ctx.color = True
        error = NoArgsIsHelpError(ctx)
        
        # Mock echo to capture the call
        echo_calls = []
        def mock_echo(message, file=None, err=True, color=None):
            echo_calls.append({
                'message': message,
                'file': file,
                'err': err,
                'color': color
            })
        
        monkeypatch.setattr('click.exceptions.echo', mock_echo)
        
        # Call show method
        test_file = io.StringIO()
        error.show(file=test_file)
        
        # Verify echo was called correctly
        assert len(echo_calls) == 1
        assert echo_calls[0]['message'] == error.format_message()
        assert echo_calls[0]['file'] == test_file
        assert echo_calls[0]['err'] == True
        assert echo_calls[0]['color'] == True

    def test_no_args_is_help_error_show_method_no_color(self, monkeypatch):
        """Test that the show method handles color=False correctly."""
        ctx = Context(Command('test_cmd'))
        ctx.color = False
        error = NoArgsIsHelpError(ctx)
        
        # Mock echo to capture the call
        echo_calls = []
        def mock_echo(message, file=None, err=True, color=None):
            echo_calls.append({
                'message': message,
                'file': file,
                'err': err,
                'color': color
            })
        
        monkeypatch.setattr('click.exceptions.echo', mock_echo)
        
        # Call show method without file parameter
        error.show()
        
        # Verify echo was called correctly
        assert len(echo_calls) == 1
        assert echo_calls[0]['message'] == error.format_message()
        assert echo_calls[0]['file'] is None
        assert echo_calls[0]['err'] == True
        assert echo_calls[0]['color'] == False
