# file: src/click/src/click/core.py:1120-1135
# asked: {"lines": [1120, 1132, 1133, 1134, 1135], "branches": []}
# gained: {"lines": [1120, 1132, 1133, 1134, 1135], "branches": []}

import pytest
from click.core import Command, Context
from click.formatting import HelpFormatter

class TestCommandFormatHelp:
    """Test cases for Command.format_help method to achieve full coverage."""
    
    def test_format_help_calls_all_format_methods(self):
        """Test that format_help calls all the required format methods."""
        # Create a mock command that tracks which methods were called
        class MockCommand(Command):
            def __init__(self):
                super().__init__(name="test_command")
                self.called_methods = []
            
            def format_usage(self, ctx, formatter):
                self.called_methods.append("format_usage")
            
            def format_help_text(self, ctx, formatter):
                self.called_methods.append("format_help_text")
            
            def format_options(self, ctx, formatter):
                self.called_methods.append("format_options")
            
            def format_epilog(self, ctx, formatter):
                self.called_methods.append("format_epilog")
        
        # Create context and formatter
        command = MockCommand()
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        # Call the method under test
        command.format_help(ctx, formatter)
        
        # Verify all methods were called in the correct order
        expected_methods = ["format_usage", "format_help_text", "format_options", "format_epilog"]
        assert command.called_methods == expected_methods
    
    def test_format_help_with_real_command(self):
        """Test format_help with a real Command instance that has help text and epilog."""
        # Create a command with help text and epilog
        command = Command(
            name="test_cmd",
            help="This is the help text for the command.",
            epilog="This is the epilog text."
        )
        
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        # Mock the individual format methods to track calls
        original_methods = {}
        called_methods = []
        
        def track_call(method_name):
            def wrapper(ctx, formatter):
                called_methods.append(method_name)
                # Call original method if it exists
                if method_name in original_methods:
                    original_methods[method_name](ctx, formatter)
            return wrapper
        
        # Replace methods with tracking versions
        original_methods["format_usage"] = command.format_usage
        original_methods["format_help_text"] = command.format_help_text
        original_methods["format_options"] = command.format_options
        original_methods["format_epilog"] = command.format_epilog
        
        command.format_usage = track_call("format_usage")
        command.format_help_text = track_call("format_help_text")
        command.format_options = track_call("format_options")
        command.format_epilog = track_call("format_epilog")
        
        # Call the method under test
        command.format_help(ctx, formatter)
        
        # Verify all methods were called
        expected_methods = ["format_usage", "format_help_text", "format_options", "format_epilog"]
        assert called_methods == expected_methods
    
    def test_format_help_with_empty_command(self):
        """Test format_help with a command that has no help text or epilog."""
        command = Command(name="empty_cmd")
        ctx = Context(command=command)
        formatter = HelpFormatter()
        
        # Mock methods to track calls
        called_methods = []
        
        def mock_format_usage(ctx, formatter):
            called_methods.append("format_usage")
        
        def mock_format_help_text(ctx, formatter):
            called_methods.append("format_help_text")
        
        def mock_format_options(ctx, formatter):
            called_methods.append("format_options")
        
        def mock_format_epilog(ctx, formatter):
            called_methods.append("format_epilog")
        
        # Replace methods with mocks
        command.format_usage = mock_format_usage
        command.format_help_text = mock_format_help_text
        command.format_options = mock_format_options
        command.format_epilog = mock_format_epilog
        
        # Call the method under test
        command.format_help(ctx, formatter)
        
        # Verify all methods were called
        expected_methods = ["format_usage", "format_help_text", "format_options", "format_epilog"]
        assert called_methods == expected_methods
