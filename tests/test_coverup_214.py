# file: src/flask/src/flask/ctx.py:104-105
# asked: {"lines": [104, 105], "branches": []}
# gained: {"lines": [104, 105], "branches": []}

import pytest
from flask.ctx import _AppCtxGlobals


class TestAppCtxGlobalsContains:
    def test_contains_returns_true_for_existing_attribute(self):
        """Test that __contains__ returns True when item exists in __dict__."""
        globals_obj = _AppCtxGlobals()
        globals_obj.test_attr = "test_value"
        
        result = "test_attr" in globals_obj
        
        assert result is True

    def test_contains_returns_false_for_missing_attribute(self):
        """Test that __contains__ returns False when item does not exist in __dict__."""
        globals_obj = _AppCtxGlobals()
        
        result = "non_existent_attr" in globals_obj
        
        assert result is False
