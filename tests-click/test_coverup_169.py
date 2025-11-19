# file: src/click/src/click/decorators.py:324-349
# asked: {"lines": [324, 325, 342, 343, 345, 346, 347, 349], "branches": [[342, 343], [342, 345]]}
# gained: {"lines": [324, 325, 342, 343, 345, 346, 347, 349], "branches": [[342, 343], [342, 345]]}

import pytest
import typing as t
from click.core import Argument
from click.decorators import argument, _param_memo

def test_argument_decorator_with_default_cls():
    """Test argument decorator with default cls (None)"""
    
    @argument('test_arg')
    def test_func(test_arg):
        return test_arg
    
    # Verify the function has the parameter attached
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, Argument)
    assert param.name == 'test_arg'

def test_argument_decorator_with_custom_cls():
    """Test argument decorator with custom cls parameter"""
    
    class CustomArgument(Argument):
        def __init__(self, param_decls, **attrs):
            super().__init__(param_decls, **attrs)
            self.custom_attr = 'custom_value'
    
    @argument('test_arg', cls=CustomArgument)
    def test_func(test_arg):
        return test_arg
    
    # Verify the function has the custom parameter attached
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, CustomArgument)
    assert param.name == 'test_arg'
    assert param.custom_attr == 'custom_value'

def test_argument_decorator_with_no_params():
    """Test argument decorator with no parameter declarations"""
    
    with pytest.raises(TypeError, match="Argument is marked as exposed, but does not have a name."):
        @argument()
        def test_func():
            pass

def test_argument_decorator_with_attrs():
    """Test argument decorator with additional attributes"""
    
    @argument('test_arg', required=False, default='default_value')
    def test_func(test_arg):
        return test_arg
    
    # Verify the function has the parameter attached with correct attributes
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, Argument)
    assert param.name == 'test_arg'
    assert param.required is False
    assert param.default == 'default_value'

def test_argument_decorator_preserves_function():
    """Test that the decorator preserves the original function"""
    
    def original_func(test_arg):
        return test_arg * 2
    
    decorated_func = argument('test_arg')(original_func)
    
    # Verify the function is preserved (same function object)
    assert decorated_func is original_func
    # Verify the function still works correctly
    assert decorated_func(5) == 10
    # Verify the parameter was attached
    assert hasattr(decorated_func, '__click_params__')
    assert len(decorated_func.__click_params__) == 1

def test_argument_decorator_with_nargs():
    """Test argument decorator with nargs attribute"""
    
    @argument('test_arg', nargs=2)
    def test_func(test_arg):
        return test_arg
    
    # Verify the function has the parameter attached with nargs
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, Argument)
    assert param.name == 'test_arg'
    assert param.nargs == 2

def test_argument_decorator_with_type():
    """Test argument decorator with type attribute"""
    
    @argument('test_arg', type=int)
    def test_func(test_arg):
        return test_arg
    
    # Verify the function has the parameter attached with type
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, Argument)
    assert param.name == 'test_arg'
    assert param.type.name == 'integer'
