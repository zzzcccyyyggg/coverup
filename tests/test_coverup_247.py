# file: src/flask/src/flask/sansio/blueprints.py:557-560
# asked: {"lines": [557, 558, 559, 560], "branches": []}
# gained: {"lines": [557, 558, 559], "branches": []}

import pytest
import typing as t
from flask.sansio.blueprints import Blueprint

T_template_global = t.TypeVar("T_template_global", bound=t.Callable[..., t.Any])

def test_app_template_global_overload_with_name_none() -> None:
    """Test the @t.overload decorator for app_template_global with name=None."""
    bp = Blueprint("test", __name__)
    
    # This should trigger the overload with name=None
    @bp.app_template_global(name=None)
    def test_global() -> str:
        return "test_value"
    
    # Verify the function was registered in deferred_functions
    assert len(bp.deferred_functions) == 1
    # The deferred function should be callable
    assert callable(bp.deferred_functions[0])

def test_app_template_global_overload_with_name_string() -> None:
    """Test the @t.overload decorator for app_template_global with a string name."""
    bp = Blueprint("test", __name__)
    
    # This should trigger the overload with a string name
    @bp.app_template_global(name="custom_global")
    def test_global() -> str:
        return "test_value"
    
    # Verify the function was registered in deferred_functions
    assert len(bp.deferred_functions) == 1
    # The deferred function should be callable
    assert callable(bp.deferred_functions[0])

def test_app_template_global_overload_without_name() -> None:
    """Test the @t.overload decorator for app_template_global without name parameter."""
    bp = Blueprint("test", __name__)
    
    # This should trigger the overload without name parameter (using function name)
    @bp.app_template_global()
    def test_global() -> str:
        return "test_value"
    
    # Verify the function was registered in deferred_functions
    assert len(bp.deferred_functions) == 1
    # The deferred function should be callable
    assert callable(bp.deferred_functions[0])

def test_app_template_global_overload_direct_call() -> None:
    """Test the @t.overload decorator for app_template_global with direct function call."""
    bp = Blueprint("test", __name__)
    
    def test_global() -> str:
        return "test_value"
    
    # This should trigger the overload with direct function call
    decorated = bp.app_template_global(name="direct_global")(test_global)
    
    # Verify the function was registered in deferred_functions and returned
    assert len(bp.deferred_functions) == 1
    # The deferred function should be callable
    assert callable(bp.deferred_functions[0])
    assert decorated is test_global
