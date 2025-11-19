# file: src/click/src/click/core.py:768-824
# asked: {"lines": [768, 788, 789, 791, 792, 793, 796, 798, 800, 801, 802, 810, 811, 812, 813, 818, 820, 822, 823, 824], "branches": [[788, 789], [788, 820], [791, 792], [791, 796], [800, 801], [800, 818], [801, 800], [801, 802], [810, 811], [810, 812]]}
# gained: {"lines": [768, 788, 789, 791, 792, 793, 796, 798, 800, 801, 802, 810, 811, 812, 813, 818, 820, 822, 823, 824], "branches": [[788, 789], [788, 820], [791, 792], [791, 796], [800, 801], [800, 818], [801, 800], [801, 802], [810, 811], [810, 812]]}

import pytest
import typing as t
from click.core import Context, Command, Option
from click.types import STRING
from click._utils import UNSET


def test_invoke_with_command_no_callback():
    """Test that invoking a Command without a callback raises TypeError."""
    cmd = Command(name="test_cmd", callback=None)
    ctx = Context(command=cmd)
    
    with pytest.raises(TypeError, match="The given command does not have a callback that can be invoked."):
        ctx.invoke(cmd)


def test_invoke_with_command_with_callback():
    """Test invoking a Command with a callback and parameters that need defaults."""
    def callback_func(value: str, optional: str = "default") -> str:
        return f"{value}-{optional}"
    
    cmd = Command(
        name="test_cmd", 
        callback=callback_func,
        params=[
            Option(["--value"], type=STRING, required=True),
            Option(["--optional"], type=STRING, required=False, expose_value=True, default="default")
        ]
    )
    ctx = Context(command=cmd)
    
    result = ctx.invoke(cmd, value="test")
    assert result == "test-default"


def test_invoke_with_command_unset_default():
    """Test invoking a Command with a parameter that has UNSET default value."""
    def callback_func(value: str, optional: t.Any) -> str:
        return f"{value}-{optional}"
    
    cmd = Command(
        name="test_cmd", 
        callback=callback_func,
        params=[
            Option(["--value"], type=STRING, required=True),
            Option(["--optional"], type=STRING, required=False, expose_value=True, default=UNSET)
        ]
    )
    ctx = Context(command=cmd)
    
    result = ctx.invoke(cmd, value="test")
    assert result == "test-None"


def test_invoke_with_command_explicit_kwargs():
    """Test invoking a Command with explicit kwargs that override defaults."""
    def callback_func(value: str, optional: str = "default") -> str:
        return f"{value}-{optional}"
    
    cmd = Command(
        name="test_cmd", 
        callback=callback_func,
        params=[
            Option(["--value"], type=STRING, required=True),
            Option(["--optional"], type=STRING, required=False, expose_value=True, default="default")
        ]
    )
    ctx = Context(command=cmd)
    
    result = ctx.invoke(cmd, value="test", optional="custom")
    assert result == "test-custom"


def test_invoke_with_command_non_exposed_param():
    """Test invoking a Command with a parameter that doesn't expose value."""
    def callback_func(value: str) -> str:
        return value
    
    cmd = Command(
        name="test_cmd", 
        callback=callback_func,
        params=[
            Option(["--value"], type=STRING, required=True),
            Option(["--hidden"], type=STRING, required=False, expose_value=False)
        ]
    )
    ctx = Context(command=cmd)
    
    result = ctx.invoke(cmd, value="test")
    assert result == "test"


def test_invoke_with_callable():
    """Test invoking a regular callable (not a Command)."""
    def simple_callback(arg1: str, arg2: int) -> str:
        return f"{arg1}-{arg2}"
    
    cmd = Command(name="dummy")
    ctx = Context(command=cmd)
    
    result = ctx.invoke(simple_callback, "hello", 42)
    assert result == "hello-42"


def test_invoke_with_callable_kwargs():
    """Test invoking a regular callable with kwargs."""
    def simple_callback(arg1: str, arg2: int = 10) -> str:
        return f"{arg1}-{arg2}"
    
    cmd = Command(name="dummy")
    ctx = Context(command=cmd)
    
    result = ctx.invoke(simple_callback, "hello", arg2=99)
    assert result == "hello-99"


def test_invoke_command_params_updated():
    """Test that ctx.params is updated with kwargs when invoking a Command."""
    def callback_func(value: str, optional: str = "default") -> str:
        return f"{value}-{optional}"
    
    cmd = Command(
        name="test_cmd", 
        callback=callback_func,
        params=[
            Option(["--value"], type=STRING, required=True),
            Option(["--optional"], type=STRING, required=False, expose_value=True, default="default")
        ]
    )
    parent_cmd = Command(name="parent")
    ctx = Context(command=parent_cmd)
    
    result = ctx.invoke(cmd, value="test", optional="custom")
    assert result == "test-custom"
