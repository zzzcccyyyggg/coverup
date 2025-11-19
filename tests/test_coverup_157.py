# file: src/flask/src/flask/ctx.py:61-65
# asked: {"lines": [61, 62, 63, 64, 65], "branches": []}
# gained: {"lines": [61, 62, 63, 64, 65], "branches": []}

import pytest
from flask.ctx import _AppCtxGlobals


class TestAppCtxGlobalsDelAttr:
    def test_delattr_existing_attribute(self):
        """Test __delattr__ when deleting an existing attribute."""
        globals_obj = _AppCtxGlobals()
        globals_obj.test_attr = "test_value"
        
        # Verify attribute exists
        assert hasattr(globals_obj, "test_attr")
        assert globals_obj.test_attr == "test_value"
        
        # Delete the attribute
        delattr(globals_obj, "test_attr")
        
        # Verify attribute is deleted
        assert not hasattr(globals_obj, "test_attr")

    def test_delattr_nonexistent_attribute(self):
        """Test __delattr__ when deleting a non-existent attribute raises AttributeError."""
        globals_obj = _AppCtxGlobals()
        
        # Verify attribute doesn't exist
        assert not hasattr(globals_obj, "nonexistent_attr")
        
        # Attempt to delete non-existent attribute should raise AttributeError
        with pytest.raises(AttributeError, match="nonexistent_attr"):
            delattr(globals_obj, "nonexistent_attr")
