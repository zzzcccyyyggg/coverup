# file: src/click/src/click/parser.py:165-178
# asked: {"lines": [165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 177, 178], "branches": [[166, 167], [166, 168], [168, 169], [168, 170], [170, 171], [170, 172], [172, 173], [172, 174], [174, 175], [174, 177]]}
# gained: {"lines": [165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 177, 178], "branches": [[166, 167], [166, 168], [168, 169], [168, 170], [170, 171], [170, 172], [172, 173], [172, 174], [174, 175], [174, 177]]}

import pytest
from click.parser import _Option, _ParsingState
from click.core import Option

class TestOptionProcess:
    def test_process_store_action(self):
        """Test _Option.process with 'store' action"""
        option = Option(['--test'])
        _option = _Option(option, ['--test'], 'test', action='store')
        state = _ParsingState([])
        
        _option.process('value', state)
        
        assert state.opts['test'] == 'value'
        assert state.order == [option]

    def test_process_store_const_action(self):
        """Test _Option.process with 'store_const' action"""
        option = Option(['--test'])
        _option = _Option(option, ['--test'], 'test', action='store_const', const='const_value')
        state = _ParsingState([])
        
        _option.process(None, state)
        
        assert state.opts['test'] == 'const_value'
        assert state.order == [option]

    def test_process_append_action(self):
        """Test _Option.process with 'append' action"""
        option = Option(['--test'])
        _option = _Option(option, ['--test'], 'test', action='append')
        state = _ParsingState([])
        
        _option.process('value1', state)
        _option.process('value2', state)
        
        assert state.opts['test'] == ['value1', 'value2']
        assert state.order == [option, option]

    def test_process_append_const_action(self):
        """Test _Option.process with 'append_const' action"""
        option = Option(['--test'])
        _option = _Option(option, ['--test'], 'test', action='append_const', const='const_value')
        state = _ParsingState([])
        
        _option.process(None, state)
        _option.process(None, state)
        
        assert state.opts['test'] == ['const_value', 'const_value']
        assert state.order == [option, option]

    def test_process_count_action(self):
        """Test _Option.process with 'count' action"""
        option = Option(['--verbose'])
        _option = _Option(option, ['--verbose'], 'verbose', action='count')
        state = _ParsingState([])
        
        _option.process(None, state)
        _option.process(None, state)
        
        assert state.opts['verbose'] == 2
        assert state.order == [option, option]

    def test_process_count_action_initial_zero(self):
        """Test _Option.process with 'count' action starting from 0"""
        option = Option(['--verbose'])
        _option = _Option(option, ['--verbose'], 'verbose', action='count')
        state = _ParsingState([])
        
        _option.process(None, state)
        
        assert state.opts['verbose'] == 1
        assert state.order == [option]

    def test_process_unknown_action(self):
        """Test _Option.process with unknown action raises ValueError"""
        option = Option(['--test'])
        _option = _Option(option, ['--test'], 'test', action='unknown_action')
        state = _ParsingState([])
        
        with pytest.raises(ValueError, match="unknown action 'unknown_action'"):
            _option.process('value', state)
        
        assert state.order == []  # Should not be added to order on error
