# file: src/flask/src/flask/sansio/blueprints.py:445-448
# asked: {"lines": [445, 446, 447, 448], "branches": []}
# gained: {"lines": [445, 446, 447], "branches": []}

import pytest
import typing as t
from flask.sansio.blueprints import Blueprint

T_template_filter = t.TypeVar("T_template_filter", bound=t.Callable)

class TestBlueprintAppTemplateFilterOverload:
    """Test cases for Blueprint.app_template_filter overload signatures."""
    
    def test_app_template_filter_decorator_with_name_none(self):
        """Test the actual decorator usage with name=None."""
        bp = Blueprint("test_bp", __name__)
        
        # Test the decorator with name=None (which should use the overload we're testing)
        @bp.app_template_filter(name=None)
        def test_filter(value: str) -> str:
            return value.upper()
        
        # Verify the filter was registered by checking deferred_functions
        assert len(bp.deferred_functions) == 1
        deferred_func = bp.deferred_functions[0]
        
        # The deferred function should be callable and related to template filters
        assert callable(deferred_func)
        
    def test_app_template_filter_decorator_without_name(self):
        """Test the decorator without name parameter (implicit None)."""
        bp = Blueprint("test_bp", __name__)
        
        # Test the decorator without name parameter (defaults to None)
        @bp.app_template_filter
        def another_filter(value: str) -> str:
            return value.lower()
        
        # Verify the filter was registered
        assert len(bp.deferred_functions) == 1
        deferred_func = bp.deferred_functions[0]
        assert callable(deferred_func)
        
    def test_app_template_filter_decorator_with_explicit_name(self):
        """Test the decorator with an explicit name string."""
        bp = Blueprint("test_bp", __name__)
        
        # Test the decorator with an explicit name
        @bp.app_template_filter(name="custom_filter")
        def custom_filter(value: str) -> str:
            return value.title()
        
        # Verify the filter was registered
        assert len(bp.deferred_functions) == 1
        deferred_func = bp.deferred_functions[0]
        assert callable(deferred_func)
