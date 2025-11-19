# file: src/flask/src/flask/globals.py:26-26
# asked: {"lines": [26], "branches": []}
# gained: {"lines": [26], "branches": []}

import pytest
import typing as t
from flask.ctx import _AppCtxGlobals


class TestAppCtxGlobalsProxy:
    def test_app_ctx_globals_proxy_class_definition(self):
        """Test that _AppCtxGlobalsProxy class definition executes line 26."""
        # Since _AppCtxGlobalsProxy is only defined in TYPE_CHECKING block,
        # we need to force TYPE_CHECKING to be True to execute the class definition
        
        # Save original TYPE_CHECKING value
        original_type_checking = t.TYPE_CHECKING
        
        try:
            # Temporarily set TYPE_CHECKING to True to execute the class definition
            t.TYPE_CHECKING = True
            
            # Re-import the module to execute the TYPE_CHECKING block
            import importlib
            import flask.globals
            importlib.reload(flask.globals)
            
            # Now the _AppCtxGlobalsProxy class should be defined
            # We can verify by checking if it exists in the module
            assert hasattr(flask.globals, '_AppCtxGlobalsProxy')
            
        finally:
            # Restore original TYPE_CHECKING value
            t.TYPE_CHECKING = original_type_checking
            # Reload module again to restore original state
            import importlib
            import flask.globals
            importlib.reload(flask.globals)
