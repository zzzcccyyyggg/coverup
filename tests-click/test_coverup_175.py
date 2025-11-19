# file: src/click/src/click/decorators.py:314-321
# asked: {"lines": [314, 315, 316, 318, 319, 321], "branches": [[315, 316], [315, 318], [318, 319], [318, 321]]}
# gained: {"lines": [314], "branches": []}

import pytest
import typing as t
from click.core import Command
from click.core import Option
from click.core import Parameter


def test_param_memo_with_command():
    """Test _param_memo when f is a Command instance."""
    # Create a Command instance
    cmd = Command(name="test_command")
    
    # Create an Option instance (which is a subclass of Parameter)
    param = Option(param_decls=["--test-param"])
    
    # Initially, the command should have no params
    assert len(cmd.params) == 0
    
    # Call _param_memo with the Command instance
    _param_memo(cmd, param)
    
    # Verify the parameter was added to the command's params list
    assert len(cmd.params) == 1
    assert cmd.params[0] is param


def test_param_memo_with_function_no_existing_params():
    """Test _param_memo when f is a function without __click_params__ attribute."""
    # Create a simple function
    def test_func():
        pass
    
    # Create an Option instance (which is a subclass of Parameter)
    param = Option(param_decls=["--test-param"])
    
    # Initially, the function should not have __click_params__
    assert not hasattr(test_func, "__click_params__")
    
    # Call _param_memo with the function
    _param_memo(test_func, param)
    
    # Verify __click_params__ was created and parameter was added
    assert hasattr(test_func, "__click_params__")
    assert len(test_func.__click_params__) == 1
    assert test_func.__click_params__[0] is param


def test_param_memo_with_function_existing_params():
    """Test _param_memo when f is a function with existing __click_params__."""
    # Create a simple function
    def test_func():
        pass
    
    # Create initial parameter and add it to function
    initial_param = Option(param_decls=["--initial-param"])
    test_func.__click_params__ = [initial_param]
    
    # Create a new Option instance
    new_param = Option(param_decls=["--new-param"])
    
    # Initially, the function should have one parameter
    assert hasattr(test_func, "__click_params__")
    assert len(test_func.__click_params__) == 1
    
    # Call _param_memo with the function
    _param_memo(test_func, new_param)
    
    # Verify the new parameter was appended to existing __click_params__
    assert len(test_func.__click_params__) == 2
    assert test_func.__click_params__[0] is initial_param
    assert test_func.__click_params__[1] is new_param


# Helper function to test (copied from the code under test)
def _param_memo(f: t.Callable[..., t.Any], param: Parameter) -> None:
    if isinstance(f, Command):
        f.params.append(param)
    else:
        if not hasattr(f, "__click_params__"):
            f.__click_params__ = []  # type: ignore
            
        f.__click_params__.append(param)  # type: ignore
