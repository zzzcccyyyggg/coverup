# file: src/click/src/click/core.py:1825-1837
# asked: {"lines": [1825, 1826, 1827, 1829, 1831, 1832, 1833, 1834, 1835, 1837], "branches": [[1826, 1827], [1826, 1829], [1831, 1832], [1831, 1834], [1834, 1835], [1834, 1837]]}
# gained: {"lines": [1825, 1826, 1827, 1829, 1831, 1832, 1833, 1834, 1835, 1837], "branches": [[1826, 1827], [1826, 1829], [1831, 1832], [1831, 1834], [1834, 1835], [1834, 1837]]}

import pytest
from click.core import Group, Context
from click.exceptions import NoArgsIsHelpError


class TestGroupParseArgs:
    """Test cases for Group.parse_args method to achieve full coverage."""
    
    def test_parse_args_no_args_is_help_raises(self):
        """Test that NoArgsIsHelpError is raised when no args and no_args_is_help is True."""
        group = Group(name='test_group', no_args_is_help=True)
        ctx = Context(group)
        
        with pytest.raises(NoArgsIsHelpError):
            group.parse_args(ctx, [])
    
    def test_parse_args_no_args_is_help_resilient_parsing(self):
        """Test that NoArgsIsHelpError is not raised when resilient_parsing is True."""
        group = Group(name='test_group', no_args_is_help=True)
        ctx = Context(group, resilient_parsing=True)
        
        # Should not raise NoArgsIsHelpError due to resilient_parsing
        result = group.parse_args(ctx, [])
        assert result == []
    
    def test_parse_args_chain_mode(self, monkeypatch):
        """Test parse_args in chain mode."""
        group = Group(name='test_group', chain=True)
        ctx = Context(group)
        
        # Mock the parent Command.parse_args to return some args
        def mock_command_parse_args(self, ctx, args):
            return ['arg1', 'arg2', 'arg3']
        
        monkeypatch.setattr('click.core.Command.parse_args', mock_command_parse_args)
        
        result = group.parse_args(ctx, ['test'])
        
        # In chain mode, protected_args should contain all rest args
        # and ctx.args should be empty
        assert ctx._protected_args == ['arg1', 'arg2', 'arg3']
        assert ctx.args == []
        assert result == []
    
    def test_parse_args_non_chain_mode_with_rest_args(self, monkeypatch):
        """Test parse_args in non-chain mode with remaining args."""
        group = Group(name='test_group', chain=False)
        ctx = Context(group)
        
        # Mock the parent Command.parse_args to return some args
        def mock_command_parse_args(self, ctx, args):
            return ['arg1', 'arg2', 'arg3']
        
        monkeypatch.setattr('click.core.Command.parse_args', mock_command_parse_args)
        
        result = group.parse_args(ctx, ['test'])
        
        # In non-chain mode, first arg goes to protected_args, rest to args
        assert ctx._protected_args == ['arg1']
        assert ctx.args == ['arg2', 'arg3']
        assert result == ['arg2', 'arg3']
    
    def test_parse_args_non_chain_mode_no_rest_args(self, monkeypatch):
        """Test parse_args in non-chain mode with no remaining args."""
        group = Group(name='test_group', chain=False)
        ctx = Context(group)
        
        # Mock the parent Command.parse_args to return empty list
        def mock_command_parse_args(self, ctx, args):
            return []
        
        monkeypatch.setattr('click.core.Command.parse_args', mock_command_parse_args)
        
        result = group.parse_args(ctx, ['test'])
        
        # With no rest args, both should be empty
        assert ctx._protected_args == []
        assert ctx.args == []
        assert result == []
