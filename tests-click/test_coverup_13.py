# file: src/click/src/click/parser.py:181-209
# asked: {"lines": [181, 182, 183, 184, 185, 187, 192, 193, 194, 195, 196, 197, 198, 199, 200, 205, 206, 208, 209], "branches": [[192, 193], [192, 205], [195, 196], [195, 197], [197, 198], [197, 205], [205, 206], [205, 208]]}
# gained: {"lines": [181, 182, 183, 184, 185, 187, 192, 193, 194, 195, 196, 197, 198, 199, 200, 205, 206, 208, 209], "branches": [[192, 193], [192, 205], [195, 196], [195, 197], [197, 198], [197, 205], [205, 206], [205, 208]]}

import pytest
from click.parser import _Argument, _ParsingState
from click._utils import UNSET
from click.exceptions import BadArgumentUsage


class TestArgument:
    def test_process_nargs_greater_than_one_all_unset(self):
        """Test when nargs > 1 and all values are UNSET."""
        mock_obj = type('MockObj', (), {})()
        arg = _Argument(mock_obj, "test_arg", nargs=3)
        state = _ParsingState([])
        
        arg.process([UNSET, UNSET, UNSET], state)
        
        assert state.opts["test_arg"] is UNSET
        assert mock_obj in state.order

    def test_process_nargs_greater_than_one_some_unset(self):
        """Test when nargs > 1 and some values are UNSET (should raise BadArgumentUsage)."""
        mock_obj = type('MockObj', (), {})()
        arg = _Argument(mock_obj, "test_arg", nargs=3)
        state = _ParsingState([])
        
        with pytest.raises(BadArgumentUsage, match="Argument 'test_arg' takes 3 values."):
            arg.process(["value1", UNSET, "value3"], state)

    def test_process_empty_tuple_value(self):
        """Test when value is an empty tuple (should be converted to UNSET)."""
        mock_obj = type('MockObj', (), {})()
        arg = _Argument(mock_obj, "test_arg", nargs=1)
        state = _ParsingState([])
        
        arg.process((), state)
        
        assert state.opts["test_arg"] is UNSET
        assert mock_obj in state.order

    def test_process_nargs_greater_than_one_no_unset(self):
        """Test when nargs > 1 and no values are UNSET."""
        mock_obj = type('MockObj', (), {})()
        arg = _Argument(mock_obj, "test_arg", nargs=2)
        state = _ParsingState([])
        
        arg.process(["value1", "value2"], state)
        
        assert state.opts["test_arg"] == ["value1", "value2"]
        assert mock_obj in state.order

    def test_process_nargs_one_with_value(self):
        """Test when nargs = 1 with a regular value."""
        mock_obj = type('MockObj', (), {})()
        arg = _Argument(mock_obj, "test_arg", nargs=1)
        state = _ParsingState([])
        
        arg.process("single_value", state)
        
        assert state.opts["test_arg"] == "single_value"
        assert mock_obj in state.order
