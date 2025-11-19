# file: src/click/src/click/parser.py:323-337
# asked: {"lines": [323, 324, 325, 326, 329, 330, 331, 332, 333, 334, 336, 337], "branches": [[324, 0], [324, 325], [329, 330], [329, 331], [331, 332], [331, 333], [333, 334], [333, 336]]}
# gained: {"lines": [323, 324, 325, 326, 329, 330, 331, 332, 333, 334, 336, 337], "branches": [[324, 0], [324, 325], [329, 330], [329, 331], [331, 332], [331, 333], [333, 334], [333, 336]]}

import pytest
from click.parser import _OptionParser, _ParsingState
from click.core import Option


class TestOptionParserProcessArgsForOptions:
    """Test cases for _OptionParser._process_args_for_options method"""

    def test_double_dash_terminates_processing(self):
        """Test that '--' terminates option processing"""
        parser = _OptionParser()
        state = _ParsingState(rargs=["--", "arg1", "arg2"])
        
        parser._process_args_for_options(state)
        
        # Should stop processing at '--' and leave remaining args in rargs
        assert state.rargs == ["arg1", "arg2"]
        assert state.largs == []

    def test_option_prefix_with_interspersed_args_disabled(self):
        """Test option processing when allow_interspersed_args is False"""
        parser = _OptionParser()
        parser.allow_interspersed_args = False
        # Add a valid option to avoid NoSuchOption errors
        option = Option(["-o", "--option"], type=str)
        parser.add_option(option, ["-o", "--option"], "option")
        state = _ParsingState(rargs=["arg1", "-o", "value"])
        
        parser._process_args_for_options(state)
        
        # Should stop at first non-option argument when interspersed args disabled
        assert state.rargs == ["arg1", "-o", "value"]
        assert state.largs == []

    def test_non_option_arg_with_interspersed_args_enabled(self):
        """Test non-option argument when allow_interspersed_args is True"""
        parser = _OptionParser()
        parser.allow_interspersed_args = True
        # Add a valid option to avoid NoSuchOption errors
        option = Option(["-o", "--option"], type=str)
        parser.add_option(option, ["-o", "--option"], "option")
        state = _ParsingState(rargs=["arg1", "-o", "value"])
        
        parser._process_args_for_options(state)
        
        # Should add non-option args to largs and continue processing
        # The option processing will consume the option and its value
        assert state.rargs == []
        assert state.largs == ["arg1"]

    def test_single_dash_not_processed_as_option(self):
        """Test that single dash '-' is not processed as an option"""
        parser = _OptionParser()
        state = _ParsingState(rargs=["-", "arg1"])
        
        parser._process_args_for_options(state)
        
        # Single dash should be treated as argument, not option
        # The method processes all args, so both should end up in largs
        assert state.rargs == []
        assert state.largs == ["-", "arg1"]

    def test_empty_string_not_processed_as_option(self):
        """Test that empty string is not processed as an option"""
        parser = _OptionParser()
        state = _ParsingState(rargs=["", "arg1"])
        
        parser._process_args_for_options(state)
        
        # Empty string should be treated as argument, not option
        # The method processes all args, so both should end up in largs
        assert state.rargs == []
        assert state.largs == ["", "arg1"]
