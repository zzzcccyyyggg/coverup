# file: src/click/src/click/core.py:979-988
# asked: {"lines": [979, 980, 981, 982, 983, 984, 985, 986, 987], "branches": []}
# gained: {"lines": [979, 980, 981, 982, 983, 984, 985, 986, 987], "branches": []}

import pytest
import click
from click.core import Command, Context

class TestCommandToInfoDict:
    """Test cases for Command.to_info_dict method to achieve full coverage."""
    
    def test_to_info_dict_with_all_attributes(self):
        """Test to_info_dict with all attributes set."""
        # Create a command with all attributes
        cmd = Command(
            name="test_command",
            help="Test help text",
            epilog="Test epilog text",
            short_help="Short help",
            hidden=True,
            deprecated="This command is deprecated"
        )
        
        # Create a mock context
        ctx = Context(cmd)
        
        # Call to_info_dict
        result = cmd.to_info_dict(ctx)
        
        # Verify all fields are present and correct
        assert result["name"] == "test_command"
        assert result["help"] == "Test help text"
        assert result["epilog"] == "Test epilog text"
        assert result["short_help"] == "Short help"
        assert result["hidden"] is True
        assert result["deprecated"] == "This command is deprecated"
        assert "params" in result
        assert isinstance(result["params"], list)
    
    def test_to_info_dict_with_none_attributes(self):
        """Test to_info_dict with None values for optional attributes."""
        # Create a command with None values for optional attributes
        cmd = Command(
            name="test_command",
            help=None,
            epilog=None,
            short_help=None,
            hidden=False,
            deprecated=False
        )
        
        # Create a mock context
        ctx = Context(cmd)
        
        # Call to_info_dict
        result = cmd.to_info_dict(ctx)
        
        # Verify all fields are present with None values
        assert result["name"] == "test_command"
        assert result["help"] is None
        assert result["epilog"] is None
        assert result["short_help"] is None
        assert result["hidden"] is False
        assert result["deprecated"] is False
        assert "params" in result
        assert isinstance(result["params"], list)
    
    def test_to_info_dict_with_params(self):
        """Test to_info_dict includes parameters from get_params."""
        # Create a command with Option parameters (which implement _parse_decls)
        cmd = Command(
            name="test_command",
            params=[
                click.Option(["--option1"]),
                click.Option(["--option2"])
            ],
            add_help_option=False  # Disable help option to get exact count
        )
        
        # Create a mock context
        ctx = Context(cmd)
        
        # Call to_info_dict
        result = cmd.to_info_dict(ctx)
        
        # Verify params list contains parameter info dicts
        assert len(result["params"]) == 2
        assert all(isinstance(param, dict) for param in result["params"])
        # Verify each parameter dict has expected structure
        for param_dict in result["params"]:
            assert "name" in param_dict
            assert "param_type_name" in param_dict
    
    def test_to_info_dict_empty_params(self):
        """Test to_info_dict with no parameters."""
        # Create a command without parameters and without help option
        cmd = Command(name="test_command", add_help_option=False)
        
        # Create a mock context
        ctx = Context(cmd)
        
        # Call to_info_dict
        result = cmd.to_info_dict(ctx)
        
        # Verify params is an empty list when no help option
        assert result["params"] == []
    
    def test_to_info_dict_with_help_option(self):
        """Test to_info_dict includes help option when add_help_option is True."""
        # Create a command with add_help_option=True (default)
        cmd = Command(name="test_command", add_help_option=True)
        
        # Create a mock context
        ctx = Context(cmd)
        
        # Call to_info_dict
        result = cmd.to_info_dict(ctx)
        
        # Should have the help option in params
        assert len(result["params"]) == 1
        # Find the help option
        help_param = result["params"][0]
        assert help_param.get("name") == "help"
    
    def test_to_info_dict_without_help_option(self):
        """Test to_info_dict excludes help option when add_help_option is False."""
        # Create a command with add_help_option=False
        cmd = Command(name="test_command", add_help_option=False)
        
        # Create a mock context
        ctx = Context(cmd)
        
        # Call to_info_dict
        result = cmd.to_info_dict(ctx)
        
        # Should not have any params when no help option and no custom params
        assert result["params"] == []
