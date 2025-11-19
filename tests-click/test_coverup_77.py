# file: src/click/src/click/core.py:1219-1253
# asked: {"lines": [1219, 1220, 1221, 1223, 1224, 1226, 1227, 1238, 1239, 1240, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1251, 1252, 1253], "branches": [[1220, 1221], [1220, 1223], [1226, 1227], [1226, 1238], [1238, 1239], [1238, 1242], [1239, 1238], [1239, 1240], [1242, 1243], [1242, 1251]]}
# gained: {"lines": [1219, 1220, 1221, 1223, 1224, 1226, 1227, 1238, 1239, 1240, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1251, 1252, 1253], "branches": [[1220, 1221], [1220, 1223], [1226, 1227], [1226, 1238], [1238, 1239], [1238, 1242], [1239, 1238], [1239, 1240], [1242, 1243], [1242, 1251]]}

import pytest
from click.core import Command, Context
from click.exceptions import NoArgsIsHelpError
from click._utils import UNSET
from unittest.mock import Mock, MagicMock


class TestCommandParseArgs:
    """Test cases for Command.parse_args method to achieve full coverage."""
    
    def test_parse_args_no_args_is_help_raises_error(self):
        """Test that NoArgsIsHelpError is raised when no_args_is_help is True and no args provided."""
        command = Command("test", no_args_is_help=True)
        ctx = Context(command)
        
        with pytest.raises(NoArgsIsHelpError):
            command.parse_args(ctx, [])
    
    def test_parse_args_no_args_is_help_resilient_parsing_no_error(self):
        """Test that NoArgsIsHelpError is not raised when resilient_parsing is True."""
        command = Command("test", no_args_is_help=True)
        ctx = Context(command, resilient_parsing=True)
        
        # Mock the parser to return empty results
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, [], [])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        result = command.parse_args(ctx, [])
        assert result == []
    
    def test_parse_args_with_args_no_error(self):
        """Test that NoArgsIsHelpError is not raised when args are provided."""
        command = Command("test", no_args_is_help=True)
        ctx = Context(command, allow_extra_args=True)  # Allow extra args to avoid failure
        
        # Mock the parser to return the args we passed in
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, ["arg1"], [])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        result = command.parse_args(ctx, ["arg1"])
        assert result == ["arg1"]
    
    def test_parse_args_converts_unset_to_none(self):
        """Test that UNSET values in ctx.params are converted to None."""
        command = Command("test")
        ctx = Context(command)
        ctx.params = {"param1": UNSET, "param2": "value", "param3": UNSET}
        
        # Mock the parser to return empty results
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, [], [])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        result = command.parse_args(ctx, [])
        
        assert ctx.params["param1"] is None
        assert ctx.params["param2"] == "value"
        assert ctx.params["param3"] is None
        assert result == []
    
    def test_parse_args_extra_args_fails_when_not_allowed(self):
        """Test that ctx.fail is called when extra args are provided and not allowed."""
        command = Command("test")
        ctx = Context(command, allow_extra_args=False)
        
        # Mock the parser to return some args
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, ["extra1", "extra2"], [])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        # Mock ctx.fail to raise an exception we can catch
        ctx.fail = Mock(side_effect=RuntimeError("fail called"))
        
        with pytest.raises(RuntimeError, match="fail called"):
            command.parse_args(ctx, [])
        
        # Verify fail was called with the expected message
        ctx.fail.assert_called_once()
        call_args = ctx.fail.call_args[0][0]
        assert "Got unexpected extra arguments" in call_args
        assert "extra1 extra2" in call_args
    
    def test_parse_args_extra_args_single_fails_when_not_allowed(self):
        """Test that ctx.fail is called with singular message for single extra arg."""
        command = Command("test")
        ctx = Context(command, allow_extra_args=False)
        
        # Mock the parser to return one extra arg
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, ["extra1"], [])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        # Mock ctx.fail to raise an exception we can catch
        ctx.fail = Mock(side_effect=RuntimeError("fail called"))
        
        with pytest.raises(RuntimeError, match="fail called"):
            command.parse_args(ctx, [])
        
        # Verify fail was called with singular message
        ctx.fail.assert_called_once()
        call_args = ctx.fail.call_args[0][0]
        assert "Got unexpected extra argument" in call_args
        assert "extra1" in call_args
    
    def test_parse_args_extra_args_allowed_no_fail(self):
        """Test that extra args don't cause failure when allow_extra_args is True."""
        command = Command("test")
        ctx = Context(command, allow_extra_args=True)
        
        # Mock the parser to return extra args
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, ["extra1", "extra2"], [])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        result = command.parse_args(ctx, [])
        
        assert result == ["extra1", "extra2"]
        assert ctx.args == ["extra1", "extra2"]
    
    def test_parse_args_resilient_parsing_extra_args_no_fail(self):
        """Test that extra args don't cause failure when resilient_parsing is True."""
        command = Command("test")
        ctx = Context(command, allow_extra_args=False, resilient_parsing=True)
        
        # Mock the parser to return extra args
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, ["extra1", "extra2"], [])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        result = command.parse_args(ctx, [])
        
        assert result == ["extra1", "extra2"]
        assert ctx.args == ["extra1", "extra2"]
    
    def test_parse_args_updates_opt_prefixes(self):
        """Test that ctx._opt_prefixes is updated with parser's _opt_prefixes."""
        command = Command("test")
        ctx = Context(command)
        
        # Mock the parser with specific opt_prefixes
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({}, [], [])
        mock_parser._opt_prefixes = {"-", "--", "+"}
        command.make_parser = Mock(return_value=mock_parser)
        
        result = command.parse_args(ctx, [])
        
        assert result == []
        assert ctx._opt_prefixes == {"-", "--", "+"}
    
    def test_parse_args_with_params_processing(self):
        """Test that parameters are processed correctly."""
        command = Command("test")
        ctx = Context(command, allow_extra_args=True)  # Allow extra args to avoid failure
        
        # Create mock parameters
        mock_param1 = Mock()
        mock_param1.handle_parse_result.return_value = (None, [])
        mock_param2 = Mock()
        mock_param2.handle_parse_result.return_value = (None, ["remaining"])
        
        # Mock the parser to return parameters for processing
        mock_parser = Mock()
        mock_parser.parse_args.return_value = ({"opt1": "val1"}, ["arg1"], [mock_param1, mock_param2])
        mock_parser._opt_prefixes = set()
        command.make_parser = Mock(return_value=mock_parser)
        
        # Mock get_params to return our mock parameters
        command.get_params = Mock(return_value=[mock_param1, mock_param2])
        
        result = command.parse_args(ctx, ["arg1"])
        
        # Verify parameters were processed
        mock_param1.handle_parse_result.assert_called_once_with(ctx, {"opt1": "val1"}, ["arg1"])
        mock_param2.handle_parse_result.assert_called_once_with(ctx, {"opt1": "val1"}, [])
        assert result == ["remaining"]
