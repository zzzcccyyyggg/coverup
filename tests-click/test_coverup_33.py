# file: src/click/src/click/exceptions.py:208-239
# asked: {"lines": [208, 209, 215, 218, 219, 220, 222, 223, 225, 226, 227, 229, 230, 231, 233, 234, 235, 236, 237, 238, 239], "branches": [[222, 223], [222, 225], [230, 231], [230, 233]]}
# gained: {"lines": [208, 209, 215, 218, 219, 220, 222, 223, 225, 226, 227, 229, 230, 231, 233, 234, 235, 236, 237, 238, 239], "branches": [[222, 223], [222, 225], [230, 231], [230, 233]]}

import pytest
from click.exceptions import NoSuchOption
from click.core import Context, Command


def test_no_such_option_init_without_message():
    """Test NoSuchOption initialization when message is None."""
    option_name = "--invalid-option"
    exception = NoSuchOption(option_name)
    
    assert exception.option_name == option_name
    assert exception.possibilities is None
    assert exception.message == "No such option: --invalid-option"


def test_no_such_option_init_with_message():
    """Test NoSuchOption initialization when message is provided."""
    option_name = "--invalid-option"
    custom_message = "Custom error message"
    exception = NoSuchOption(option_name, message=custom_message)
    
    assert exception.option_name == option_name
    assert exception.possibilities is None
    assert exception.message == custom_message


def test_no_such_option_init_with_possibilities():
    """Test NoSuchOption initialization with possibilities."""
    option_name = "--invalid-option"
    possibilities = ["--valid-option1", "--valid-option2"]
    exception = NoSuchOption(option_name, possibilities=possibilities)
    
    assert exception.option_name == option_name
    assert exception.possibilities == possibilities


def test_no_such_option_init_with_context():
    """Test NoSuchOption initialization with context."""
    option_name = "--invalid-option"
    command = Command("test_command")
    ctx = Context(command)
    exception = NoSuchOption(option_name, ctx=ctx)
    
    assert exception.option_name == option_name
    assert exception.ctx == ctx


def test_no_such_option_format_message_no_possibilities():
    """Test format_message when no possibilities are provided."""
    option_name = "--invalid-option"
    exception = NoSuchOption(option_name)
    
    formatted_message = exception.format_message()
    assert formatted_message == "No such option: --invalid-option"


def test_no_such_option_format_message_with_single_possibility():
    """Test format_message with a single possibility."""
    option_name = "--invalid-option"
    possibilities = ["--valid-option"]
    exception = NoSuchOption(option_name, possibilities=possibilities)
    
    formatted_message = exception.format_message()
    expected = "No such option: --invalid-option Did you mean --valid-option?"
    assert formatted_message == expected


def test_no_such_option_format_message_with_multiple_possibilities():
    """Test format_message with multiple possibilities."""
    option_name = "--invalid-option"
    possibilities = ["--valid-option1", "--valid-option2", "--valid-option3"]
    exception = NoSuchOption(option_name, possibilities=possibilities)
    
    formatted_message = exception.format_message()
    expected = "No such option: --invalid-option (Possible options: --valid-option1, --valid-option2, --valid-option3)"
    assert formatted_message == expected


def test_no_such_option_format_message_with_sorted_possibilities():
    """Test format_message ensures possibilities are sorted."""
    option_name = "--invalid-option"
    possibilities = ["--z-option", "--a-option", "--m-option"]
    exception = NoSuchOption(option_name, possibilities=possibilities)
    
    formatted_message = exception.format_message()
    expected = "No such option: --invalid-option (Possible options: --a-option, --m-option, --z-option)"
    assert formatted_message == expected


def test_no_such_option_format_message_with_custom_message_and_possibilities():
    """Test format_message with custom message and possibilities."""
    option_name = "--invalid-option"
    custom_message = "Custom error message"
    possibilities = ["--valid-option1", "--valid-option2"]
    exception = NoSuchOption(option_name, message=custom_message, possibilities=possibilities)
    
    formatted_message = exception.format_message()
    expected = "Custom error message (Possible options: --valid-option1, --valid-option2)"
    assert formatted_message == expected
