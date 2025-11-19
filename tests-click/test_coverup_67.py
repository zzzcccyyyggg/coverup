# file: src/click/src/click/decorators.py:51-97
# asked: {"lines": [51, 52, 76, 77, 78, 81, 82, 84, 86, 87, 88, 89, 93, 95, 97], "branches": [[81, 82], [81, 84], [86, 87], [86, 93]]}
# gained: {"lines": [51, 52, 76, 77, 78, 81, 82, 84, 86, 87, 88, 89, 93, 95, 97], "branches": [[81, 82], [81, 84], [86, 87], [86, 93]]}

import pytest
import click
from click.decorators import make_pass_decorator
from click.globals import get_current_context

class TestObject:
    def __init__(self, value="default"):
        self.value = value

def test_make_pass_decorator_with_ensure_false_and_object_found():
    """Test make_pass_decorator with ensure=False when object exists in context."""
    ctx = click.Context(click.Command('test'))
    test_obj = TestObject("test_value")
    ctx.obj = test_obj
    
    @make_pass_decorator(TestObject, ensure=False)
    def callback(obj, arg1, arg2):
        return f"{obj.value}-{arg1}-{arg2}"
    
    with ctx:
        result = callback("hello", "world")
        assert result == "test_value-hello-world"

def test_make_pass_decorator_with_ensure_false_and_object_not_found():
    """Test make_pass_decorator with ensure=False when object doesn't exist in context."""
    ctx = click.Context(click.Command('test'))
    
    @make_pass_decorator(TestObject, ensure=False)
    def callback(obj, arg1, arg2):
        return f"{obj.value}-{arg1}-{arg2}"
    
    with ctx:
        with pytest.raises(RuntimeError) as exc_info:
            callback("hello", "world")
        assert "Managed to invoke callback without a context object of type 'TestObject' existing." in str(exc_info.value)

def test_make_pass_decorator_with_ensure_true_and_object_not_found():
    """Test make_pass_decorator with ensure=True when object doesn't exist in context."""
    ctx = click.Context(click.Command('test'))
    
    @make_pass_decorator(TestObject, ensure=True)
    def callback(obj, arg1, arg2):
        return f"{obj.value}-{arg1}-{arg2}"
    
    with ctx:
        result = callback("hello", "world")
        assert result == "default-hello-world"

def test_make_pass_decorator_with_ensure_true_and_object_exists():
    """Test make_pass_decorator with ensure=True when object already exists in context."""
    ctx = click.Context(click.Command('test'))
    test_obj = TestObject("existing_value")
    ctx.obj = test_obj
    
    @make_pass_decorator(TestObject, ensure=True)
    def callback(obj, arg1, arg2):
        return f"{obj.value}-{arg1}-{arg2}"
    
    with ctx:
        result = callback("hello", "world")
        assert result == "existing_value-hello-world"

def test_make_pass_decorator_wrapper_properties():
    """Test that the decorator properly wraps the function."""
    def original_func(obj, arg1, arg2):
        """Original function docstring."""
        return f"{obj.value}-{arg1}-{arg2}"
    
    ctx = click.Context(click.Command('test'))
    test_obj = TestObject("test_value")
    ctx.obj = test_obj
    
    decorated_func = make_pass_decorator(TestObject)(original_func)
    
    with ctx:
        result = decorated_func("hello", "world")
        assert result == "test_value-hello-world"
        assert decorated_func.__name__ == original_func.__name__
        assert decorated_func.__doc__ == original_func.__doc__
