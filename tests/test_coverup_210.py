# file: src/flask/src/flask/ctx.py:58-59
# asked: {"lines": [58, 59], "branches": []}
# gained: {"lines": [58, 59], "branches": []}

import pytest
import typing as t
from flask.ctx import _AppCtxGlobals


class TestAppCtxGlobals:
    def test_setattr_sets_attribute(self):
        """Test that __setattr__ sets the attribute in the instance dictionary."""
        globals_obj = _AppCtxGlobals()
        
        # Set an attribute using __setattr__
        globals_obj.__setattr__("test_attr", "test_value")
        
        # Verify the attribute was set in the instance dictionary
        assert globals_obj.__dict__["test_attr"] == "test_value"
        
        # Also verify it can be accessed via regular attribute access
        assert globals_obj.test_attr == "test_value"
