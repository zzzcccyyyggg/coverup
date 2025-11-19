# file: src/click/src/click/parser.py:261-284
# asked: {"lines": [261, 266, 267, 268, 278, 279, 280, 281, 282, 283, 284], "branches": [[281, 282], [281, 283], [283, 0], [283, 284]]}
# gained: {"lines": [261, 266, 267, 268, 278, 279, 280, 281, 282, 283, 284], "branches": [[281, 282], [281, 283], [283, 0], [283, 284]]}

import pytest
from click.core import Context, Option, Command
from click.parser import _OptionParser

class TestOptionParserAddOption:
    """Test cases for _OptionParser.add_option method to achieve full coverage."""
    
    def test_add_option_with_short_and_long_opts(self):
        """Test adding an option with both short and long forms."""
        parser = _OptionParser()
        obj = Option(['-f', '--file'], help='File option')
        
        parser.add_option(obj, ['-f', '--file'], 'file')
        
        assert '-f' in parser._short_opt
        assert '--file' in parser._long_opt
        assert parser._short_opt['-f'] is parser._long_opt['--file']
        # The parser initializes with {'-', '--'} and adds prefixes from options
        assert '-' in parser._opt_prefixes
        assert '--' in parser._opt_prefixes
    
    def test_add_option_with_only_short_opts(self):
        """Test adding an option with only short forms."""
        parser = _OptionParser()
        obj = Option(['-a', '-b'], help='Short options')
        
        parser.add_option(obj, ['-a', '-b'], 'short_opts')
        
        assert '-a' in parser._short_opt
        assert '-b' in parser._short_opt
        assert len(parser._long_opt) == 0
        # The parser initializes with {'-', '--'} and adds prefixes from options
        assert '-' in parser._opt_prefixes
        assert '--' in parser._opt_prefixes
    
    def test_add_option_with_only_long_opts(self):
        """Test adding an option with only long forms."""
        parser = _OptionParser()
        obj = Option(['--verbose', '--debug'], help='Long options')
        
        parser.add_option(obj, ['--verbose', '--debug'], 'long_opts')
        
        assert '--verbose' in parser._long_opt
        assert '--debug' in parser._long_opt
        assert len(parser._short_opt) == 0
        # The parser initializes with {'-', '--'} and adds prefixes from options
        assert '-' in parser._opt_prefixes
        assert '--' in parser._opt_prefixes
    
    def test_add_option_with_custom_action(self):
        """Test adding an option with custom action."""
        parser = _OptionParser()
        obj = Option(['-c'], help='Count option')
        
        parser.add_option(obj, ['-c'], 'count', action='count', nargs=0)
        
        assert '-c' in parser._short_opt
        option = parser._short_opt['-c']
        assert option.action == 'count'
        assert option.nargs == 0
    
    def test_add_option_with_store_const_action(self):
        """Test adding an option with store_const action."""
        parser = _OptionParser()
        obj = Option(['--flag'], help='Flag option')
        
        parser.add_option(obj, ['--flag'], 'flag', action='store_const', const=True)
        
        assert '--flag' in parser._long_opt
        option = parser._long_opt['--flag']
        assert option.action == 'store_const'
        assert option.const is True
    
    def test_add_option_with_append_action(self):
        """Test adding an option with append action."""
        parser = _OptionParser()
        obj = Option(['-a'], help='Append option')
        
        parser.add_option(obj, ['-a'], 'append', action='append')
        
        assert '-a' in parser._short_opt
        option = parser._short_opt['-a']
        assert option.action == 'append'
    
    def test_add_option_with_append_const_action(self):
        """Test adding an option with append_const action."""
        parser = _OptionParser()
        obj = Option(['--add-default'], help='Append const option')
        
        parser.add_option(obj, ['--add-default'], 'defaults', action='append_const', const='default')
        
        assert '--add-default' in parser._long_opt
        option = parser._long_opt['--add-default']
        assert option.action == 'append_const'
        assert option.const == 'default'
    
    def test_add_option_with_nargs_greater_than_one(self):
        """Test adding an option with nargs > 1."""
        parser = _OptionParser()
        obj = Option(['-m'], help='Multiple values')
        
        parser.add_option(obj, ['-m'], 'multi', nargs=3)
        
        assert '-m' in parser._short_opt
        option = parser._short_opt['-m']
        assert option.nargs == 3
    
    def test_add_option_with_nargs_zero(self):
        """Test adding an option with nargs = 0."""
        parser = _OptionParser()
        obj = Option(['-v'], help='Verbose flag')
        
        parser.add_option(obj, ['-v'], 'verbose', nargs=0)
        
        assert '-v' in parser._short_opt
        option = parser._short_opt['-v']
        assert option.nargs == 0
    
    def test_add_option_with_context_token_normalization(self):
        """Test adding an option with context token normalization."""
        def normalize_token(token):
            return token.upper()
        
        # Create a minimal command to pass to Context
        cmd = Command('test_cmd')
        ctx = Context(cmd)
        ctx.token_normalize_func = normalize_token
        parser = _OptionParser(ctx)
        obj = Option(['--file-name'], help='File option')
        
        parser.add_option(obj, ['--file-name'], 'file')
        
        # The normalized option should be in the long opts
        assert '--FILE-NAME' in parser._long_opt
        assert parser._long_opt['--FILE-NAME'].obj is obj
