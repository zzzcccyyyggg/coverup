# file: src/click/src/click/core.py:1081-1086
# asked: {"lines": [1081, 1083, 1084, 1085, 1086], "branches": [[1084, 1085], [1084, 1086]]}
# gained: {"lines": [1081, 1083, 1084, 1085, 1086], "branches": [[1084, 1085], [1084, 1086]]}

import pytest
import click
from click.core import Command, Context
from click.parser import _OptionParser

class TestCommandMakeParser:
    def test_make_parser_creates_parser_with_params(self):
        """Test that make_parser creates a parser and adds all parameters."""
        # Create a command with some parameters
        cmd = Command(name="test_command")
        
        # Create a mock parameter that can be added to parser
        class MockParam:
            def __init__(self):
                self.opts = ['--test-option']
            
            def add_to_parser(self, parser, ctx):
                # This method should be called for each parameter
                pass
        
        # Mock the get_params method to return our test parameters
        mock_params = [MockParam(), MockParam()]
        cmd.get_params = lambda ctx: mock_params
        
        # Create a context
        ctx = Context(cmd)
        
        # Call make_parser
        parser = cmd.make_parser(ctx)
        
        # Verify the parser was created
        assert isinstance(parser, _OptionParser)
        assert parser.ctx is ctx

    def test_make_parser_with_no_params(self):
        """Test that make_parser works correctly when there are no parameters."""
        cmd = Command(name="test_command")
        
        # Mock get_params to return empty list
        cmd.get_params = lambda ctx: []
        
        ctx = Context(cmd)
        
        parser = cmd.make_parser(ctx)
        
        assert isinstance(parser, _OptionParser)
        assert parser.ctx is ctx

    def test_make_parser_calls_add_to_parser_for_each_param(self, monkeypatch):
        """Test that add_to_parser is called for each parameter."""
        cmd = Command(name="test_command")
        
        # Track calls to add_to_parser
        calls = []
        
        class MockParam:
            def __init__(self, name):
                self.name = name
                self.opts = [f'--{name}']
            
            def add_to_parser(self, parser, ctx):
                calls.append((self.name, parser, ctx))
        
        mock_params = [MockParam("param1"), MockParam("param2")]
        cmd.get_params = lambda ctx: mock_params
        
        ctx = Context(cmd)
        
        parser = cmd.make_parser(ctx)
        
        # Verify add_to_parser was called for each parameter
        assert len(calls) == 2
        assert calls[0][0] == "param1"
        assert calls[1][0] == "param2"
        assert calls[0][1] is parser
        assert calls[0][2] is ctx
        assert calls[1][1] is parser
        assert calls[1][2] is ctx
