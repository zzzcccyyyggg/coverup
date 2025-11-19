# file: src/click/src/click/decorators.py:39-48
# asked: {"lines": [39, 45, 46, 48], "branches": []}
# gained: {"lines": [39, 45, 46, 48], "branches": []}

import pytest
from click.decorators import pass_obj
from click import Context
from click.core import BaseCommand
from unittest.mock import Mock

class TestPassObj:
    
    def test_pass_obj_decorator_with_context_obj(self, monkeypatch):
        """Test that pass_obj correctly passes context.obj to the decorated function"""
        # Create a mock context with an obj attribute
        mock_context = Mock()
        mock_context.obj = "test_object"
        
        # Mock get_current_context to return our mock context
        monkeypatch.setattr('click.decorators.get_current_context', lambda: mock_context)
        
        # Create a test function that we'll decorate
        def target_function(obj, arg1, arg2):
            return f"{obj}-{arg1}-{arg2}"
        
        # Apply the decorator
        decorated_func = pass_obj(target_function)
        
        # Call the decorated function with arguments
        result = decorated_func("arg1_value", "arg2_value")
        
        # Verify the result
        assert result == "test_object-arg1_value-arg2_value"
        
    def test_pass_obj_decorator_with_none_context_obj(self, monkeypatch):
        """Test that pass_obj handles None context.obj correctly"""
        # Create a mock context with None obj
        mock_context = Mock()
        mock_context.obj = None
        
        # Mock get_current_context to return our mock context
        monkeypatch.setattr('click.decorators.get_current_context', lambda: mock_context)
        
        # Create a test function that we'll decorate
        def target_function(obj, arg1, arg2):
            return f"obj_is_{obj}-{arg1}-{arg2}"
        
        # Apply the decorator
        decorated_func = pass_obj(target_function)
        
        # Call the decorated function with arguments
        result = decorated_func("arg1_value", "arg2_value")
        
        # Verify the result
        assert result == "obj_is_None-arg1_value-arg2_value"
        
    def test_pass_obj_decorator_with_complex_object(self, monkeypatch):
        """Test that pass_obj works with complex objects in context.obj"""
        # Create a complex object for context.obj
        class ComplexObj:
            def __init__(self, name, value):
                self.name = name
                self.value = value
            
            def __str__(self):
                return f"{self.name}:{self.value}"
        
        complex_obj = ComplexObj("test", 42)
        
        # Create a mock context with the complex object
        mock_context = Mock()
        mock_context.obj = complex_obj
        
        # Mock get_current_context to return our mock context
        monkeypatch.setattr('click.decorators.get_current_context', lambda: mock_context)
        
        # Create a test function that uses the complex object
        def target_function(obj, prefix):
            return f"{prefix}_{obj.name}_{obj.value}"
        
        # Apply the decorator
        decorated_func = pass_obj(target_function)
        
        # Call the decorated function
        result = decorated_func("result")
        
        # Verify the result
        assert result == "result_test_42"
        
    def test_pass_obj_wrapper_attributes(self, monkeypatch):
        """Test that update_wrapper properly copies attributes from the original function"""
        # Create a mock context
        mock_context = Mock()
        mock_context.obj = "test_obj"
        monkeypatch.setattr('click.decorators.get_current_context', lambda: mock_context)
        
        # Create a test function with specific attributes
        def original_function(obj, arg):
            return f"{obj}-{arg}"
        
        original_function.__name__ = "original_function"
        original_function.__doc__ = "This is a test function"
        
        # Apply the decorator
        decorated_func = pass_obj(original_function)
        
        # Verify that wrapper attributes are properly set
        assert decorated_func.__name__ == "original_function"
        assert decorated_func.__doc__ == "This is a test function"
        
        # Also verify the function still works correctly
        result = decorated_func("test_arg")
        assert result == "test_obj-test_arg"
