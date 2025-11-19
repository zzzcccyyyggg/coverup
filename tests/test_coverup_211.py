# file: src/flask/src/flask/ctx.py:107-108
# asked: {"lines": [107, 108], "branches": []}
# gained: {"lines": [107, 108], "branches": []}

import pytest
import typing as t
from flask.ctx import _AppCtxGlobals

class TestAppCtxGlobals:
    def test_iter_returns_dict_keys_iterator(self):
        """Test that __iter__ returns an iterator over the object's attribute names."""
        globals_obj = _AppCtxGlobals()
        globals_obj.test_attr = "test_value"
        globals_obj.another_attr = 123
        
        iterator = iter(globals_obj)
        result = list(iterator)
        
        assert "test_attr" in result
        assert "another_attr" in result
        assert len(result) == 2
