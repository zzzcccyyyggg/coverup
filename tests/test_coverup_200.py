# file: src/flask/src/flask/sansio/scaffold.py:42-49
# asked: {"lines": [42, 43, 45, 46, 47, 49], "branches": []}
# gained: {"lines": [42, 43, 45, 46, 47, 49], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold, setupmethod
from typing import Any, cast

class TestScaffold(Scaffold):
    """Test implementation of Scaffold that allows setup methods to be called."""
    
    def __init__(self, import_name: str):
        super().__init__(import_name)
        self._setup_finished = False
    
    def _check_setup_finished(self, f_name: str) -> None:
        """Override to allow setup methods to be called during testing."""
        pass

def test_setupmethod_decorator():
    """Test that setupmethod decorator properly wraps functions."""
    
    class TestClass(TestScaffold):
        def __init__(self):
            super().__init__("test_module")
        
        @setupmethod
        def test_method(self, arg1: Any, arg2: Any = None) -> str:
            return f"called with {arg1} and {arg2}"
    
    # Create instance and call the decorated method
    instance = TestClass()
    result = instance.test_method("hello", arg2="world")
    
    # Verify the method was called correctly
    assert result == "called with hello and world"
    
    # Test with different arguments
    result2 = instance.test_method("test")
    assert result2 == "called with test and None"

def test_setupmethod_with_positional_and_keyword_args():
    """Test setupmethod with various argument combinations."""
    
    class TestClass(TestScaffold):
        def __init__(self):
            super().__init__("test_module")
        
        @setupmethod
        def complex_method(self, a: Any, b: Any, *args: Any, **kwargs: Any) -> tuple:
            return (a, b, args, kwargs)
    
    instance = TestClass()
    
    # Test with positional arguments only
    result = instance.complex_method(1, 2)
    assert result == (1, 2, (), {})
    
    # Test with extra positional arguments
    result = instance.complex_method(1, 2, 3, 4)
    assert result == (1, 2, (3, 4), {})
    
    # Test with keyword arguments
    result = instance.complex_method(1, 2, x=10, y=20)
    assert result == (1, 2, (), {'x': 10, 'y': 20})
    
    # Test with mixed arguments
    result = instance.complex_method(1, 2, 3, 4, x=10, y=20)
    assert result == (1, 2, (3, 4), {'x': 10, 'y': 20})

def test_setupmethod_function_name_preservation():
    """Test that setupmethod preserves the original function's name and attributes."""
    
    class TestClass(TestScaffold):
        def __init__(self):
            super().__init__("test_module")
        
        @setupmethod
        def original_method(self) -> str:
            """This is a docstring."""
            return "original"
    
    instance = TestClass()
    
    # Verify the wrapper has the same name as the original
    assert instance.original_method.__name__ == "original_method"
    
    # Verify the method works correctly
    result = instance.original_method()
    assert result == "original"

def test_setupmethod_return_type():
    """Test that setupmethod properly handles return types."""
    
    class TestClass(TestScaffold):
        def __init__(self):
            super().__init__("test_module")
        
        @setupmethod
        def returns_none(self) -> None:
            pass
        
        @setupmethod
        def returns_int(self) -> int:
            return 42
        
        @setupmethod
        def returns_dict(self) -> dict:
            return {"key": "value"}
    
    instance = TestClass()
    
    # Test None return
    result = instance.returns_none()
    assert result is None
    
    # Test int return
    result = instance.returns_int()
    assert result == 42
    assert isinstance(result, int)
    
    # Test dict return
    result = instance.returns_dict()
    assert result == {"key": "value"}
    assert isinstance(result, dict)

def test_setupmethod_wrapper_attributes():
    """Test that setupmethod wrapper has proper attributes from functools.update_wrapper."""
    
    class TestClass(TestScaffold):
        def __init__(self):
            super().__init__("test_module")
        
        @setupmethod
        def documented_method(self) -> str:
            """This method has a docstring."""
            return "documented"
    
    instance = TestClass()
    
    # Verify the wrapper preserves the original function's attributes
    assert instance.documented_method.__name__ == "documented_method"
    assert instance.documented_method.__doc__ == "This method has a docstring."
    assert callable(instance.documented_method)
