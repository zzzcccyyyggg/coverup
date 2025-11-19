# file: src/flask/src/flask/cli.py:120-197
# asked: {"lines": [120, 124, 128, 129, 130, 131, 132, 133, 135, 136, 137, 138, 139, 141, 142, 143, 146, 149, 150, 151, 152, 153, 154, 156, 159, 160, 161, 163, 164, 167, 168, 169, 170, 171, 172, 176, 177, 178, 179, 180, 181, 183, 184, 185, 187, 189, 191, 192, 194, 195, 196], "branches": [[135, 136], [135, 139], [139, 141], [139, 163], [141, 142], [141, 146], [176, 177], [176, 189], [180, 181], [180, 183], [191, 192], [191, 194]]}
# gained: {"lines": [120, 124, 128, 129, 130, 131, 132, 133, 135, 136, 137, 138, 139, 141, 142, 143, 146, 149, 150, 151, 153, 156, 159, 160, 161, 163, 164, 167, 168, 169, 170, 171, 172, 176, 177, 178, 179, 180, 181, 183, 184, 185, 187, 189, 191, 194, 195, 196], "branches": [[135, 136], [135, 139], [139, 141], [139, 163], [141, 142], [141, 146], [176, 177], [176, 189], [180, 181], [180, 183], [191, 194]]}

import ast
import pytest
from types import ModuleType
from flask import Flask
from flask.cli import find_app_by_string, NoAppException

def test_find_app_by_string_syntax_error():
    """Test that a SyntaxError in app_name raises NoAppException."""
    module = ModuleType("test_module")
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(module, "invalid syntax @#$")
    
    assert "Failed to parse" in str(exc_info.value)

def test_find_app_by_string_call_with_non_name_func():
    """Test that a Call with non-Name func raises NoAppException."""
    module = ModuleType("test_module")
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(module, "obj.method()")
    
    assert "Function reference must be a simple name" in str(exc_info.value)

def test_find_app_by_string_call_with_invalid_args():
    """Test that invalid arguments in function call raise NoAppException."""
    module = ModuleType("test_module")
    
    def test_func():
        return Flask(__name__)
    
    module.test_func = test_func
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(module, "test_func(invalid_arg)")
    
    assert "Failed to parse arguments as literal values" in str(exc_info.value)

def test_find_app_by_string_invalid_expression():
    """Test that non-Name and non-Call expressions raise NoAppException."""
    module = ModuleType("test_module")
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(module, "1 + 2")
    
    assert "Failed to parse" in str(exc_info.value)

def test_find_app_by_string_attribute_not_found():
    """Test that missing attribute raises NoAppException."""
    module = ModuleType("test_module")
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(module, "nonexistent")
    
    assert "Failed to find attribute" in str(exc_info.value)

def test_find_app_by_string_function_wrong_args():
    """Test that function with wrong arguments raises NoAppException."""
    module = ModuleType("test_module")
    
    def create_app(x, y):
        return Flask(__name__)
    
    module.create_app = create_app
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(module, "create_app()")
    
    assert "could not be called with the specified arguments" in str(exc_info.value)

def test_find_app_by_string_non_flask_object():
    """Test that non-Flask object raises NoAppException."""
    module = ModuleType("test_module")
    
    class NotAFlaskApp:
        pass
    
    module.app = NotAFlaskApp()
    
    with pytest.raises(NoAppException) as exc_info:
        find_app_by_string(module, "app")
    
    assert "A valid Flask application was not obtained" in str(exc_info.value)

def test_find_app_by_string_function_type_error_not_wrong_args():
    """Test that function TypeError not due to wrong args is re-raised."""
    module = ModuleType("test_module")
    
    def failing_func():
        raise TypeError("Some internal error")
    
    module.failing_func = failing_func
    
    with pytest.raises(TypeError, match="Some internal error"):
        find_app_by_string(module, "failing_func()")
