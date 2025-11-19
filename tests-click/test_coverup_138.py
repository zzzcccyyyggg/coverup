# file: src/click/src/click/decorators.py:352-377
# asked: {"lines": [352, 353, 370, 371, 373, 374, 375, 377], "branches": [[370, 371], [370, 373]]}
# gained: {"lines": [352, 353, 370, 371, 373, 374, 375, 377], "branches": [[370, 371], [370, 373]]}

import pytest
import typing as t
from click.core import Option
from click.decorators import option, _param_memo

def test_option_decorator_with_default_cls():
    """Test option decorator with default cls (None)"""
    
    @option('--test-option', help='Test option')
    def test_func():
        return "test"
    
    # Verify the function has the parameter attached
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, Option)
    assert param.name == 'test_option'
    assert param.help == 'Test option'

def test_option_decorator_with_custom_cls():
    """Test option decorator with custom cls parameter"""
    
    class CustomOption(Option):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.custom_attr = "custom"
    
    @option('--custom-option', cls=CustomOption, help='Custom option')
    def test_func():
        return "test"
    
    # Verify the function has the custom parameter attached
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, CustomOption)
    assert param.name == 'custom_option'
    assert param.help == 'Custom option'
    assert param.custom_attr == "custom"

def test_option_decorator_multiple_params():
    """Test option decorator with multiple parameter declarations"""
    
    @option('-t', '--test', '--test-alias', help='Multiple declarations')
    def test_func():
        return "test"
    
    # Verify the function has the parameter attached
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, Option)
    assert param.name == 'test'
    assert param.opts == ['-t', '--test', '--test-alias']
    assert param.help == 'Multiple declarations'

def test_option_decorator_with_additional_attrs():
    """Test option decorator with additional attributes passed to Option"""
    
    @option('--count', type=int, default=0, help='Count option')
    def test_func():
        return "test"
    
    # Verify the function has the parameter attached with additional attrs
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert isinstance(param, Option)
    assert param.name == 'count'
    assert param.type.name == 'integer'
    assert param.default == 0
    assert param.help == 'Count option'

def test_option_decorator_preserves_function_behavior():
    """Test that the decorator preserves the original function behavior"""
    
    @option('--value', type=int)
    def test_func(value=0):
        return value + 1
    
    # Test that the function still works normally
    result = test_func(value=5)
    assert result == 6
    
    # And that it has the parameter attached
    assert hasattr(test_func, '__click_params__')
    assert len(test_func.__click_params__) == 1
    param = test_func.__click_params__[0]
    assert param.name == 'value'
