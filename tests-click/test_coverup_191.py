# file: src/click/src/click/parser.py:212-217
# asked: {"lines": [212, 213, 214, 215, 216, 217], "branches": []}
# gained: {"lines": [212, 213, 214, 215, 216, 217], "branches": []}

import pytest
from click.parser import _ParsingState


class TestParsingState:
    def test_init_with_empty_rargs(self):
        """Test _ParsingState initialization with empty rargs list."""
        rargs = []
        state = _ParsingState(rargs)
        
        assert state.opts == {}
        assert state.largs == []
        assert state.rargs == rargs
        assert state.order == []
    
    def test_init_with_non_empty_rargs(self):
        """Test _ParsingState initialization with non-empty rargs list."""
        rargs = ["arg1", "arg2", "arg3"]
        state = _ParsingState(rargs)
        
        assert state.opts == {}
        assert state.largs == []
        assert state.rargs == rargs
        assert state.order == []
    
    def test_init_rargs_is_same_object(self):
        """Test that rargs is the same list object passed to constructor."""
        rargs = ["test_arg"]
        state = _ParsingState(rargs)
        
        assert state.rargs is rargs
        assert id(state.rargs) == id(rargs)
