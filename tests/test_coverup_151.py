# file: src/flask/src/flask/ctx.py:52-56
# asked: {"lines": [52, 53, 54, 55, 56], "branches": []}
# gained: {"lines": [52, 53, 54, 55, 56], "branches": []}

import pytest
import typing as t
from flask.ctx import _AppCtxGlobals


class TestAppCtxGlobals:
    def test_getattr_raises_attribute_error_for_missing_attribute(self):
        """Test that __getattr__ raises AttributeError for missing attributes."""
        globals_obj = _AppCtxGlobals()
        
        with pytest.raises(AttributeError) as exc_info:
            _ = globals_obj.nonexistent_attribute
            
        assert str(exc_info.value) == "nonexistent_attribute"
