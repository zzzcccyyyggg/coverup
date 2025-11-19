# file: src/flask/src/flask/ctx.py:67-76
# asked: {"lines": [67, 76], "branches": []}
# gained: {"lines": [67, 76], "branches": []}

import pytest
from flask.ctx import _AppCtxGlobals

class TestAppCtxGlobalsGet:
    def test_get_existing_attribute(self):
        """Test getting an existing attribute returns its value."""
        globals_obj = _AppCtxGlobals()
        globals_obj.test_attr = "test_value"
        
        result = globals_obj.get("test_attr")
        assert result == "test_value"
    
    def test_get_non_existing_attribute_with_default(self):
        """Test getting a non-existing attribute with default returns default."""
        globals_obj = _AppCtxGlobals()
        
        result = globals_obj.get("non_existing", "default_value")
        assert result == "default_value"
    
    def test_get_non_existing_attribute_without_default(self):
        """Test getting a non-existing attribute without default returns None."""
        globals_obj = _AppCtxGlobals()
        
        result = globals_obj.get("non_existing")
        assert result is None
