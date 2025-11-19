# file: src/click/src/click/parser.py:312-321
# asked: {"lines": [312, 313, 314, 317, 318, 320, 321], "branches": [[317, 318], [317, 320]]}
# gained: {"lines": [312, 313, 314, 317, 318, 320, 321], "branches": [[317, 318], [317, 320]]}

import pytest
from click.parser import _OptionParser, _ParsingState, _Argument
from click.core import Argument
from click._utils import UNSET


class TestOptionParserProcessArgsForArgs:
    def test_process_args_for_args_with_multiple_arguments(self, monkeypatch):
        """Test _process_args_for_args with multiple arguments having different nargs."""
        parser = _OptionParser()
        
        # Create mock arguments with different nargs
        arg1 = Argument(["arg1"])
        arg2 = Argument(["arg2"])
        arg3 = Argument(["arg3"])
        
        parser._args = [
            _Argument(arg1, "arg1", nargs=1),
            _Argument(arg2, "arg2", nargs=2),
            _Argument(arg3, "arg3", nargs=1)
        ]
        
        # Create state with enough arguments for all nargs
        # Note: _unpack_args processes state.largs + state.rargs
        state = _ParsingState(rargs=["val1", "val2a", "val2b", "val3", "extra1", "extra2"])
        state.largs = ["left1", "left2"]
        
        # Mock the process method to track calls
        process_calls = []
        def mock_process(value, state_ref):
            process_calls.append(value)
        
        # Patch all argument process methods
        for arg in parser._args:
            monkeypatch.setattr(arg, "process", mock_process)
        
        # Call the method under test
        parser._process_args_for_args(state)
        
        # Verify process was called with correct values
        # _unpack_args processes left1, left2, val1, val2a, val2b, val3, extra1, extra2
        # nargs: [1, 2, 1] so:
        # - first arg gets left1 (nargs=1)
        # - second arg gets (left2, val1) (nargs=2)  
        # - third arg gets val2a (nargs=1)
        assert process_calls == ["left1", ("left2", "val1"), "val2a"]
        
        # Verify state was updated correctly
        # Remaining args: val2b, val3, extra1, extra2
        assert state.largs == ["val2b", "val3", "extra1", "extra2"]
        assert state.rargs == []

    def test_process_args_for_args_with_unset_values(self, monkeypatch):
        """Test _process_args_for_args when some arguments get UNSET values."""
        parser = _OptionParser()
        
        # Create mock arguments where some won't get values
        arg1 = Argument(["arg1"])
        arg2 = Argument(["arg2"])
        
        parser._args = [
            _Argument(arg1, "arg1", nargs=2),  # Needs 2 args
            _Argument(arg2, "arg2", nargs=1)   # Needs 1 arg
        ]
        
        # Create state with insufficient arguments for first arg
        # _unpack_args processes state.largs + state.rargs
        state = _ParsingState(rargs=["only_one_value"])
        state.largs = ["existing_left"]
        
        # Mock the process method to track calls
        process_calls = []
        def mock_process(value, state_ref):
            process_calls.append(value)
        
        # Patch all argument process methods
        for arg in parser._args:
            monkeypatch.setattr(arg, "process", mock_process)
        
        # Call the method under test
        parser._process_args_for_args(state)
        
        # Verify process was called with UNSET values for missing args
        # _unpack_args processes existing_left, only_one_value
        # nargs: [2, 1] so:
        # - first arg gets (existing_left, only_one_value) (nargs=2)
        # - second arg gets UNSET (nargs=1, no more args)
        assert len(process_calls) == 2
        assert process_calls[0] == ("existing_left", "only_one_value")
        assert process_calls[1] == UNSET
        
        # Verify state was updated correctly
        assert state.largs == []
        assert state.rargs == []

    def test_process_args_for_args_with_no_arguments(self):
        """Test _process_args_for_args when there are no arguments defined."""
        parser = _OptionParser()
        parser._args = []
        
        state = _ParsingState(rargs=["val1", "val2"])
        state.largs = ["left1"]
        
        # This should not raise any errors
        parser._process_args_for_args(state)
        
        # Verify state was updated correctly
        # All largs + rargs become new largs, rargs cleared
        assert state.largs == ["left1", "val1", "val2"]
        assert state.rargs == []

    def test_process_args_for_args_with_variable_nargs(self, monkeypatch):
        """Test _process_args_for_args with variable nargs including negative values."""
        parser = _OptionParser()
        
        # Create arguments with various nargs including -1 (consume all remaining)
        arg1 = Argument(["arg1"])
        arg2 = Argument(["arg2"])
        arg3 = Argument(["arg3"])
        
        parser._args = [
            _Argument(arg1, "arg1", nargs=1),
            _Argument(arg2, "arg2", nargs=-1),  # Consume all remaining
            _Argument(arg3, "arg3", nargs=1)    # This should get UNSET
        ]
        
        # _unpack_args processes state.largs + state.rargs
        state = _ParsingState(rargs=["val1", "val2a", "val2b", "val2c"])
        state.largs = ["initial_left"]
        
        # Mock the process method to track calls
        process_calls = []
        def mock_process(value, state_ref):
            process_calls.append(value)
        
        # Patch all argument process methods
        for arg in parser._args:
            monkeypatch.setattr(arg, "process", mock_process)
        
        # Call the method under test
        parser._process_args_for_args(state)
        
        # Verify process was called with correct values
        # _unpack_args processes initial_left, val1, val2a, val2b, val2c
        # nargs: [1, -1, 1] so:
        # - first arg gets initial_left (nargs=1)
        # - second arg gets (val1, val2a, val2b) (nargs=-1, consumes all remaining except what's needed for next args)
        # - third arg gets val2c (nargs=1)
        assert process_calls == ["initial_left", ("val1", "val2a", "val2b"), "val2c"]
        
        # Verify state was updated correctly
        assert state.largs == []
        assert state.rargs == []

    def test_process_args_for_args_with_only_rargs(self, monkeypatch):
        """Test _process_args_for_args when there are no largs, only rargs."""
        parser = _OptionParser()
        
        # Create mock arguments
        arg1 = Argument(["arg1"])
        arg2 = Argument(["arg2"])
        
        parser._args = [
            _Argument(arg1, "arg1", nargs=1),
            _Argument(arg2, "arg2", nargs=2)
        ]
        
        # Only rargs, no largs
        state = _ParsingState(rargs=["val1", "val2a", "val2b", "extra"])
        state.largs = []
        
        # Mock the process method to track calls
        process_calls = []
        def mock_process(value, state_ref):
            process_calls.append(value)
        
        # Patch all argument process methods
        for arg in parser._args:
            monkeypatch.setattr(arg, "process", mock_process)
        
        # Call the method under test
        parser._process_args_for_args(state)
        
        # Verify process was called with correct values
        # _unpack_args processes val1, val2a, val2b, extra
        # nargs: [1, 2] so:
        # - first arg gets val1 (nargs=1)
        # - second arg gets (val2a, val2b) (nargs=2)
        assert process_calls == ["val1", ("val2a", "val2b")]
        
        # Verify state was updated correctly
        assert state.largs == ["extra"]
        assert state.rargs == []

    def test_process_args_for_args_with_negative_nargs_only(self, monkeypatch):
        """Test _process_args_for_args with only a negative nargs argument."""
        parser = _OptionParser()
        
        # Create argument with nargs=-1 (consume all remaining)
        arg1 = Argument(["arg1"])
        
        parser._args = [
            _Argument(arg1, "arg1", nargs=-1)
        ]
        
        # _unpack_args processes state.largs + state.rargs
        state = _ParsingState(rargs=["val1", "val2", "val3"])
        state.largs = ["left1", "left2"]
        
        # Mock the process method to track calls
        process_calls = []
        def mock_process(value, state_ref):
            process_calls.append(value)
        
        # Patch all argument process methods
        for arg in parser._args:
            monkeypatch.setattr(arg, "process", mock_process)
        
        # Call the method under test
        parser._process_args_for_args(state)
        
        # Verify process was called with correct values
        # _unpack_args processes left1, left2, val1, val2, val3
        # nargs: [-1] so:
        # - first arg gets (left1, left2, val1, val2, val3) (nargs=-1, consumes all)
        assert process_calls == [("left1", "left2", "val1", "val2", "val3")]
        
        # Verify state was updated correctly
        assert state.largs == []
        assert state.rargs == []
