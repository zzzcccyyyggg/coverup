# file: src/click/src/click/decorators.py:168-255
# asked: {"lines": [168, 169, 170, 206, 208, 209, 210, 211, 212, 214, 215, 217, 218, 219, 221, 222, 224, 225, 226, 227, 229, 230, 232, 233, 235, 236, 237, 239, 240, 242, 243, 245, 246, 248, 249, 250, 252, 253, 255], "branches": [[208, 209], [208, 214], [214, 215], [214, 217], [218, 219], [218, 221], [232, 233], [232, 235], [235, 236], [235, 239], [239, 240], [239, 242], [245, 246], [245, 248], [252, 253], [252, 255]]}
# gained: {"lines": [168, 169, 170, 206, 208, 209, 210, 211, 212, 214, 215, 217, 218, 219, 221, 222, 224, 225, 226, 227, 229, 230, 232, 233, 235, 239, 240, 242, 243, 245, 246, 248, 249, 250, 252, 253, 255], "branches": [[208, 209], [208, 214], [214, 215], [214, 217], [218, 219], [218, 221], [232, 233], [232, 235], [235, 239], [239, 240], [239, 242], [245, 246], [245, 248], [252, 253], [252, 255]]}

import pytest
import typing as t
from click.core import Command
from click.decorators import command

def test_command_decorator_with_callable_name():
    """Test when name is a callable (lines 208-212)"""
    def test_func():
        return "test"
    
    # This should trigger the callable name path
    cmd = command(test_func)
    assert isinstance(cmd, Command)
    assert cmd.callback is test_func
    # The name should be generated from the function name
    assert cmd.name == "test-func"

def test_command_decorator_with_cls_and_callable_name_raises():
    """Test assertion when cls is provided with callable name (line 211)"""
    class CustomCommand(Command):
        pass
    
    def test_func():
        return "test"
    
    with pytest.raises(AssertionError, match="Use 'command\\(cls=cls\\)\\(callable\\)' to specify a class"):
        command(test_func, cls=CustomCommand)

def test_command_decorator_with_attrs_and_callable_name_raises():
    """Test assertion when attrs are provided with callable name (line 212)"""
    def test_func():
        return "test"
    
    with pytest.raises(AssertionError, match="Use 'command\\(\\*\\*kwargs\\)\\(callable\\)' to provide arguments"):
        command(test_func, help="test help")

def test_command_decorator_with_custom_cls():
    """Test when custom cls is provided (lines 214-215)"""
    class CustomCommand(Command):
        pass
    
    @command(cls=CustomCommand)
    def test_func():
        """Test function"""
        return "test"
    
    assert isinstance(test_func, CustomCommand)
    # The callback should be the original function, not the command object
    assert test_func.callback.__name__ == "test_func"
    assert test_func.name == "test-func"

def test_command_decorator_with_existing_command_raises():
    """Test when trying to convert a command twice (lines 218-219)"""
    @command
    def test_func():
        return "test"
    
    with pytest.raises(TypeError, match="Attempted to convert a callback into a command twice"):
        command(test_func)

def test_command_decorator_with_params_attribute():
    """Test when function has __click_params__ attribute (lines 224-230)"""
    from click import Option
    
    def test_func():
        return "test"
    
    # Mock __click_params__ attribute
    test_func.__click_params__ = [Option(['--test'], help="test option")]
    
    cmd = command(test_func)
    assert isinstance(cmd, Command)
    assert len(cmd.params) == 1
    assert cmd.params[0].opts == ['--test']
    # Verify __click_params__ was deleted
    assert not hasattr(test_func, '__click_params__')

def test_command_decorator_with_help_from_docstring():
    """Test when help is not provided and taken from docstring (lines 232-233)"""
    @command
    def test_func():
        """This is a test function"""
        return "test"
    
    assert test_func.help == "This is a test function"

def test_command_decorator_with_explicit_help():
    """Test when explicit help is provided (line 232)"""
    @command(help="Explicit help")
    def test_func():
        """This should be ignored"""
        return "test"
    
    assert test_func.help == "Explicit help"

def test_command_decorator_with_explicit_name():
    """Test when explicit name is provided (lines 239-240)"""
    @command(name="custom-name")
    def test_func():
        return "test"
    
    assert test_func.name == "custom-name"

def test_command_decorator_name_generation_with_suffix():
    """Test name generation with suffix removal (lines 242-246)"""
    @command
    def test_command():
        return "test"
    
    assert test_command.name == "test"
    
    @command
    def test_cmd():
        return "test"
    
    assert test_cmd.name == "test"
    
    @command
    def test_group():
        return "test"
    
    assert test_group.name == "test"
    
    @command
    def test_grp():
        return "test"
    
    assert test_grp.name == "test"

def test_command_decorator_name_generation_without_suffix():
    """Test name generation without suffix removal (lines 242-246)"""
    @command
    def test_function():
        return "test"
    
    assert test_function.name == "test-function"
    
    @command
    def my_command_test():
        return "test"
    
    assert my_command_test.name == "my-command-test"

def test_command_decorator_with_params_argument():
    """Test when params argument is provided (lines 221-222)"""
    from click import Option
    
    test_option = Option(['--test'], help="test option")
    
    @command(params=[test_option])
    def test_func():
        return "test"
    
    assert isinstance(test_func, Command)
    assert len(test_func.params) == 1
    assert test_func.params[0] is test_option

def test_command_decorator_with_params_attr_and_click_params():
    """Test when both params attr and __click_params__ exist (lines 221-230)"""
    from click import Option
    
    def test_func():
        return "test"
    
    # Set up both params attribute and __click_params__
    test_func.__click_params__ = [Option(['--click-param'], help="from click params")]
    attr_option = Option(['--attr-param'], help="from attrs")
    
    # Use the decorator pattern to pass params
    cmd_decorator = command(params=[attr_option])
    cmd = cmd_decorator(test_func)
    
    # Both params should be included, with click params appended
    assert len(cmd.params) == 2
    # Check by option names instead of parameter names
    assert cmd.params[0].opts == ['--attr-param']
    assert cmd.params[1].opts == ['--click-param']
    assert not hasattr(test_func, '__click_params__')

def test_command_decorator_docstring_preservation():
    """Test that docstring is preserved on the command (line 249)"""
    @command
    def test_func():
        """Original docstring"""
        return "test"
    
    assert test_func.__doc__ == "Original docstring"

def test_command_decorator_without_parentheses():
    """Test decorator usage without parentheses (line 252-253)"""
    @command
    def test_func():
        return "test"
    
    assert isinstance(test_func, Command)
    assert test_func.name == "test-func"

def test_command_decorator_with_parentheses():
    """Test decorator usage with parentheses (line 255)"""
    @command()
    def test_func():
        return "test"
    
    assert isinstance(test_func, Command)
    assert test_func.name == "test-func"
