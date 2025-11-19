# file: src/flask/src/flask/ctx.py:432-480
# asked: {"lines": [452, 457, 458, 462, 463, 464], "branches": [[451, 452], [456, 457], [461, 462]]}
# gained: {"lines": [452, 457, 458, 462, 463, 464], "branches": [[451, 452], [456, 457], [461, 462]]}

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.globals import _cv_app


class TestAppContextPop:
    """Test cases for AppContext.pop method to achieve full coverage."""
    
    def test_pop_not_pushed_raises_runtime_error(self):
        """Test that popping an AppContext that was never pushed raises RuntimeError."""
        app = Flask(__name__)
        ctx = AppContext(app)
        
        with pytest.raises(RuntimeError, match="Cannot pop this context.*it is not pushed"):
            ctx.pop()
    
    def test_pop_no_active_context_raises_runtime_error(self):
        """Test that popping when there's no active context raises RuntimeError."""
        app = Flask(__name__)
        ctx = AppContext(app)
        
        # Push the context to get a token
        ctx.push()
        
        # Manually reset the context variable to simulate no active context
        _cv_app.reset(ctx._cv_token)
        
        # Now try to pop - should raise RuntimeError about no active context
        with pytest.raises(RuntimeError, match="Cannot pop this context.*there is no active context"):
            ctx.pop()
    
    def test_pop_wrong_active_context_raises_runtime_error(self):
        """Test that popping when a different context is active raises RuntimeError."""
        app = Flask(__name__)
        ctx1 = AppContext(app)
        ctx2 = AppContext(app)
        
        # Push both contexts
        ctx1.push()
        ctx2.push()
        
        # Now ctx2 is active, try to pop ctx1 while ctx2 is active
        with pytest.raises(RuntimeError, match="Cannot pop this context.*it is not the active context"):
            ctx1.pop()
        
        # Clean up by popping ctx2
        ctx2.pop()
