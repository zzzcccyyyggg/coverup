# file: src/flask/src/flask/sansio/blueprints.py:499-502
# asked: {"lines": [499, 500, 501, 502], "branches": []}
# gained: {"lines": [499, 500, 501], "branches": []}

import pytest
import typing as t
from flask.sansio.blueprints import Blueprint

T_template_test = t.TypeVar("T_template_test", bound=t.Callable[..., bool])

class TestBlueprintAppTemplateTestOverload:
    """Test cases for Blueprint.app_template_test overload with name parameter."""
    
    def test_app_template_test_overload_with_name_none(self):
        """Test the @t.overload for app_template_test with name=None."""
        # This test verifies that the type signature for the overload exists
        # The actual implementation is tested through the main method
        bp = Blueprint("test_bp", __name__)
        
        # The overload signature should be callable with name=None
        # This test ensures the overload is present and type-checkable
        def dummy_test(value: t.Any) -> bool:
            return isinstance(value, str)
        
        # This would be the usage pattern that matches the overload
        decorated = bp.app_template_test(name=None)(dummy_test)
        assert decorated is dummy_test
        
    def test_app_template_test_overload_with_name_string(self):
        """Test the @t.overload for app_template_test with name as string."""
        bp = Blueprint("test_bp", __name__)
        
        # The overload signature should be callable with a string name
        def dummy_test(value: t.Any) -> bool:
            return value is not None
        
        # This would be the usage pattern that matches the overload
        decorated = bp.app_template_test(name="custom_test")(dummy_test)
        assert decorated is dummy_test
