# file: src/click/src/click/core.py:3390-3391
# asked: {"lines": [3390, 3391], "branches": []}
# gained: {"lines": [3390, 3391], "branches": []}

import pytest
from click.core import Argument
from click.parser import _OptionParser
from click import Context
from click import Command


class TestArgumentAddToParser:
    def test_add_to_parser_calls_add_argument(self, monkeypatch):
        """Test that Argument.add_to_parser calls parser.add_argument with correct parameters."""
        # Create a mock parser
        mock_parser = _OptionParser()
        
        # Track calls to add_argument
        add_argument_calls = []
        original_add_argument = mock_parser.add_argument
        
        def mock_add_argument(obj, dest, nargs):
            add_argument_calls.append({
                'obj': obj,
                'dest': dest,
                'nargs': nargs
            })
            return original_add_argument(obj, dest, nargs)
        
        monkeypatch.setattr(mock_parser, 'add_argument', mock_add_argument)
        
        # Create an Argument instance with a single-element list
        argument = Argument(['test_arg'], nargs=1)
        
        # Create a mock context with a mock command
        mock_command = Command('test_command')
        ctx = Context(mock_command)
        
        # Call the method under test
        argument.add_to_parser(mock_parser, ctx)
        
        # Verify the call was made with correct parameters
        assert len(add_argument_calls) == 1
        assert add_argument_calls[0]['obj'] == argument
        assert add_argument_calls[0]['dest'] == 'test_arg'
        assert add_argument_calls[0]['nargs'] == 1

    def test_add_to_parser_with_different_nargs(self, monkeypatch):
        """Test that Argument.add_to_parser handles different nargs values correctly."""
        # Create a mock parser
        mock_parser = _OptionParser()
        
        # Track calls to add_argument
        add_argument_calls = []
        original_add_argument = mock_parser.add_argument
        
        def mock_add_argument(obj, dest, nargs):
            add_argument_calls.append({
                'obj': obj,
                'dest': dest,
                'nargs': nargs
            })
            return original_add_argument(obj, dest, nargs)
        
        monkeypatch.setattr(mock_parser, 'add_argument', mock_add_argument)
        
        # Test with nargs=-1 (unlimited arguments)
        argument = Argument(['test_arg'], nargs=-1)
        mock_command = Command('test_command')
        ctx = Context(mock_command)
        
        argument.add_to_parser(mock_parser, ctx)
        
        assert len(add_argument_calls) == 1
        assert add_argument_calls[0]['nargs'] == -1
        assert add_argument_calls[0]['dest'] == 'test_arg'
        assert add_argument_calls[0]['obj'] == argument

    def test_add_to_parser_with_nargs_zero(self, monkeypatch):
        """Test that Argument.add_to_parser handles nargs=0 correctly."""
        # Create a mock parser
        mock_parser = _OptionParser()
        
        # Track calls to add_argument
        add_argument_calls = []
        original_add_argument = mock_parser.add_argument
        
        def mock_add_argument(obj, dest, nargs):
            add_argument_calls.append({
                'obj': obj,
                'dest': dest,
                'nargs': nargs
            })
            return original_add_argument(obj, dest, nargs)
        
        monkeypatch.setattr(mock_parser, 'add_argument', mock_add_argument)
        
        # Test with nargs=0
        argument = Argument(['test_arg'], nargs=0)
        mock_command = Command('test_command')
        ctx = Context(mock_command)
        
        argument.add_to_parser(mock_parser, ctx)
        
        assert len(add_argument_calls) == 1
        assert add_argument_calls[0]['nargs'] == 0
        assert add_argument_calls[0]['dest'] == 'test_arg'
        assert add_argument_calls[0]['obj'] == argument
