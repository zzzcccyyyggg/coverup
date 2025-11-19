# file: src/click/src/click/core.py:1035-1044
# asked: {"lines": [1035, 1039, 1041, 1042, 1044], "branches": [[1041, 1042], [1041, 1044]]}
# gained: {"lines": [1035, 1039, 1041, 1042, 1044], "branches": [[1041, 1042], [1041, 1044]]}

import pytest
import click
from click.core import Command, Context, Option, Argument

class TestCommandCollectUsagePieces:
    """Test cases for Command.collect_usage_pieces method"""
    
    def test_collect_usage_pieces_with_options_metavar(self):
        """Test collect_usage_pieces when options_metavar is set"""
        # Create a command with options_metavar
        cmd = Command('test_cmd', options_metavar='[OPTIONS]')
        ctx = Context(cmd)
        
        # Mock get_params to return empty list
        cmd.get_params = lambda ctx: []
        
        result = cmd.collect_usage_pieces(ctx)
        
        # Should include the options_metavar
        assert result == ['[OPTIONS]']
    
    def test_collect_usage_pieces_without_options_metavar(self):
        """Test collect_usage_pieces when options_metavar is None"""
        # Create a command without options_metavar
        cmd = Command('test_cmd', options_metavar=None)
        ctx = Context(cmd)
        
        # Mock get_params to return empty list
        cmd.get_params = lambda ctx: []
        
        result = cmd.collect_usage_pieces(ctx)
        
        # Should be empty list when no options_metavar and no params
        assert result == []
    
    def test_collect_usage_pieces_with_params(self):
        """Test collect_usage_pieces with parameters that have usage pieces"""
        # Create a command with options_metavar
        cmd = Command('test_cmd', options_metavar='[OPTIONS]')
        ctx = Context(cmd)
        
        # Create real parameters that will have usage pieces
        param1 = Argument(['arg1'])
        param2 = Option(['--option1'])
        
        # Mock get_params to return our parameters
        cmd.get_params = lambda ctx: [param1, param2]
        
        result = cmd.collect_usage_pieces(ctx)
        
        # Should include options_metavar and all parameter usage pieces
        # Arguments typically show as <arg1>, options don't show in usage pieces
        assert '[OPTIONS]' in result
        assert len(result) >= 1  # At least options_metavar
    
    def test_collect_usage_pieces_with_params_no_options_metavar(self):
        """Test collect_usage_pieces with parameters but no options_metavar"""
        # Create a command without options_metavar
        cmd = Command('test_cmd', options_metavar=None)
        ctx = Context(cmd)
        
        # Create real parameters that will have usage pieces
        param1 = Argument(['arg1'])
        param2 = Argument(['arg2'])
        
        # Mock get_params to return our parameters
        cmd.get_params = lambda ctx: [param1, param2]
        
        result = cmd.collect_usage_pieces(ctx)
        
        # Should include only parameter usage pieces
        assert len(result) >= 2  # At least two arguments
    
    def test_collect_usage_pieces_empty_params_with_options_metavar(self):
        """Test collect_usage_pieces with empty params list but with options_metavar"""
        # Create a command with options_metavar
        cmd = Command('test_cmd', options_metavar='[OPTIONS]')
        ctx = Context(cmd)
        
        # Mock get_params to return empty list
        cmd.get_params = lambda ctx: []
        
        result = cmd.collect_usage_pieces(ctx)
        
        # Should include only options_metavar
        assert result == ['[OPTIONS]']
    
    def test_collect_usage_pieces_params_with_empty_usage_pieces(self):
        """Test collect_usage_pieces with parameters that return empty usage pieces"""
        # Create a command with options_metavar
        cmd = Command('test_cmd', options_metavar='[OPTIONS]')
        ctx = Context(cmd)
        
        # Create mock parameters that return empty usage pieces
        class MockParam:
            def get_usage_pieces(self, ctx):
                return []
        
        param1 = MockParam()
        param2 = MockParam()
        
        # Mock get_params to return our mock parameters
        cmd.get_params = lambda ctx: [param1, param2]
        
        result = cmd.collect_usage_pieces(ctx)
        
        # Should include only options_metavar since params have no usage pieces
        assert result == ['[OPTIONS]']
    
    def test_collect_usage_pieces_mixed_params(self):
        """Test collect_usage_pieces with mixed parameters (some with usage pieces, some without)"""
        # Create a command with options_metavar
        cmd = Command('test_cmd', options_metavar='[OPTIONS]')
        ctx = Context(cmd)
        
        # Create mock parameters - one with usage pieces, one without
        class MockParamWithPieces:
            def get_usage_pieces(self, ctx):
                return ['<arg>']
        
        class MockParamWithoutPieces:
            def get_usage_pieces(self, ctx):
                return []
        
        param1 = MockParamWithPieces()
        param2 = MockParamWithoutPieces()
        
        # Mock get_params to return our mock parameters
        cmd.get_params = lambda ctx: [param1, param2]
        
        result = cmd.collect_usage_pieces(ctx)
        
        # Should include options_metavar and usage pieces from param1
        assert result == ['[OPTIONS]', '<arg>']
