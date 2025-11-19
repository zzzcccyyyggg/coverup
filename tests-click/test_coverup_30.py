# file: src/click/src/click/core.py:935-977
# asked: {"lines": [935, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 954, 956, 957, 960, 964, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977], "branches": [[956, 957], [956, 960]]}
# gained: {"lines": [935, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 954, 956, 957, 960, 964, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977], "branches": [[956, 957], [956, 960]]}

import pytest
import click
from click.core import Command, Context, Option


def test_command_init_with_all_parameters():
    """Test Command.__init__ with all parameters to cover lines 935-977."""
    
    def dummy_callback():
        pass
    
    params = [Option(["--test-param"])]
    
    cmd = Command(
        name="test_command",
        context_settings={"max_content_width": 80},
        callback=dummy_callback,
        params=params,
        help="Test help text",
        epilog="Test epilog text",
        short_help="Short help",
        options_metavar="[CUSTOM_OPTIONS]",
        add_help_option=False,
        no_args_is_help=True,
        hidden=True,
        deprecated="This command is deprecated"
    )
    
    assert cmd.name == "test_command"
    assert cmd.context_settings == {"max_content_width": 80}
    assert cmd.callback == dummy_callback
    assert len(cmd.params) == 1
    assert cmd.help == "Test help text"
    assert cmd.epilog == "Test epilog text"
    assert cmd.options_metavar == "[CUSTOM_OPTIONS]"
    assert cmd.short_help == "Short help"
    assert cmd.add_help_option is False
    assert cmd.no_args_is_help is True
    assert cmd.hidden is True
    assert cmd.deprecated == "This command is deprecated"


def test_command_init_with_none_context_settings():
    """Test Command.__init__ with None context_settings to cover line 956-957."""
    
    cmd = Command(
        name="test_command",
        context_settings=None,
        callback=None,
        params=None,
        help=None,
        epilog=None,
        short_help=None,
        options_metavar=None,
        add_help_option=True,
        no_args_is_help=False,
        hidden=False,
        deprecated=False
    )
    
    assert cmd.name == "test_command"
    assert cmd.context_settings == {}
    assert cmd.callback is None
    assert cmd.params == []
    assert cmd.help is None
    assert cmd.epilog is None
    assert cmd.options_metavar is None
    assert cmd.short_help is None
    assert cmd.add_help_option is True
    assert cmd.no_args_is_help is False
    assert cmd.hidden is False
    assert cmd.deprecated is False


def test_command_init_with_empty_params():
    """Test Command.__init__ with empty params list to cover line 968."""
    
    cmd = Command(
        name="test_command",
        params=[]
    )
    
    assert cmd.params == []


def test_command_init_with_deprecated_string():
    """Test Command.__init__ with deprecated as string to cover line 977."""
    
    cmd = Command(
        name="test_command",
        deprecated="Custom deprecation message"
    )
    
    assert cmd.deprecated == "Custom deprecation message"


def test_command_init_with_deprecated_true():
    """Test Command.__init__ with deprecated as True to cover line 977."""
    
    cmd = Command(
        name="test_command",
        deprecated=True
    )
    
    assert cmd.deprecated is True


def test_command_init_minimal_parameters():
    """Test Command.__init__ with minimal parameters to cover default values."""
    
    cmd = Command(name="minimal_command")
    
    assert cmd.name == "minimal_command"
    assert cmd.context_settings == {}
    assert cmd.callback is None
    assert cmd.params == []
    assert cmd.help is None
    assert cmd.epilog is None
    assert cmd.options_metavar == "[OPTIONS]"
    assert cmd.short_help is None
    assert cmd.add_help_option is True
    assert cmd.no_args_is_help is False
    assert cmd.hidden is False
    assert cmd.deprecated is False
