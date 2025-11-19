# file: src/flask/src/flask/ctx.py:92-102
# asked: {"lines": [92, 102], "branches": []}
# gained: {"lines": [92, 102], "branches": []}

import pytest
from flask.ctx import _AppCtxGlobals

class TestAppCtxGlobalsSetdefault:
    def test_setdefault_existing_attribute(self):
        """Test setdefault when attribute already exists."""
        globals_obj = _AppCtxGlobals()
        globals_obj.test_attr = "existing_value"
        
        result = globals_obj.setdefault("test_attr", "default_value")
        
        assert result == "existing_value"
        assert globals_obj.test_attr == "existing_value"

    def test_setdefault_new_attribute(self):
        """Test setdefault when attribute does not exist."""
        globals_obj = _AppCtxGlobals()
        
        result = globals_obj.setdefault("new_attr", "default_value")
        
        assert result == "default_value"
        assert globals_obj.new_attr == "default_value"

    def test_setdefault_new_attribute_none_default(self):
        """Test setdefault when attribute does not exist and default is None."""
        globals_obj = _AppCtxGlobals()
        
        result = globals_obj.setdefault("new_attr", None)
        
        assert result is None
        assert globals_obj.new_attr is None
