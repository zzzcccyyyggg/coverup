# file: src/flask/src/flask/ctx.py:78-90
# asked: {"lines": [78, 87, 88, 90], "branches": [[87, 88], [87, 90]]}
# gained: {"lines": [78, 87, 88, 90], "branches": [[87, 88], [87, 90]]}

import pytest
import typing as t
from flask.ctx import _AppCtxGlobals, _sentinel


class TestAppCtxGlobalsPop:
    """Test cases for _AppCtxGlobals.pop method to achieve full coverage."""
    
    def test_pop_without_default_raises_keyerror(self):
        """Test pop without default when key doesn't exist raises KeyError."""
        globals_obj = _AppCtxGlobals()
        
        with pytest.raises(KeyError):
            globals_obj.pop("nonexistent_key")
    
    def test_pop_without_default_success(self):
        """Test pop without default when key exists returns value."""
        globals_obj = _AppCtxGlobals()
        globals_obj.test_key = "test_value"
        
        result = globals_obj.pop("test_key")
        
        assert result == "test_value"
        assert not hasattr(globals_obj, "test_key")
    
    def test_pop_with_default_when_key_exists(self):
        """Test pop with default when key exists returns value."""
        globals_obj = _AppCtxGlobals()
        globals_obj.test_key = "test_value"
        
        result = globals_obj.pop("test_key", "default_value")
        
        assert result == "test_value"
        assert not hasattr(globals_obj, "test_key")
    
    def test_pop_with_default_when_key_does_not_exist(self):
        """Test pop with default when key doesn't exist returns default."""
        globals_obj = _AppCtxGlobals()
        
        result = globals_obj.pop("nonexistent_key", "default_value")
        
        assert result == "default_value"
