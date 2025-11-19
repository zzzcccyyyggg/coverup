# file: src/click/src/click/parser.py:286-292
# asked: {"lines": [286, 292], "branches": []}
# gained: {"lines": [286, 292], "branches": []}

import pytest
from click.core import Argument
from click.parser import _OptionParser, _Argument


class TestOptionParserAddArgument:
    """Test cases for _OptionParser.add_argument method."""
    
    def test_add_argument_with_dest_and_nargs(self):
        """Test add_argument with explicit dest and nargs."""
        parser = _OptionParser()
        arg_obj = Argument(['test_arg'])
        
        parser.add_argument(arg_obj, dest='test_dest', nargs=2)
        
        assert len(parser._args) == 1
        added_arg = parser._args[0]
        assert isinstance(added_arg, _Argument)
        assert added_arg.obj is arg_obj
        assert added_arg.dest == 'test_dest'
        assert added_arg.nargs == 2
    
    def test_add_argument_with_none_dest(self):
        """Test add_argument with None dest."""
        parser = _OptionParser()
        arg_obj = Argument(['test_arg'])
        
        parser.add_argument(arg_obj, dest=None, nargs=1)
        
        assert len(parser._args) == 1
        added_arg = parser._args[0]
        assert isinstance(added_arg, _Argument)
        assert added_arg.obj is arg_obj
        assert added_arg.dest is None
        assert added_arg.nargs == 1
    
    def test_add_argument_default_nargs(self):
        """Test add_argument with default nargs value."""
        parser = _OptionParser()
        arg_obj = Argument(['test_arg'])
        
        parser.add_argument(arg_obj, dest='test_dest')
        
        assert len(parser._args) == 1
        added_arg = parser._args[0]
        assert isinstance(added_arg, _Argument)
        assert added_arg.obj is arg_obj
        assert added_arg.dest == 'test_dest'
        assert added_arg.nargs == 1
