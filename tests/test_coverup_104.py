# file: src/flask/src/flask/ctx.py:117-147
# asked: {"lines": [117, 138, 140, 141, 142, 146, 147], "branches": [[140, 141], [140, 146]]}
# gained: {"lines": [117, 138, 140, 141, 142, 146, 147], "branches": [[140, 141], [140, 146]]}

import pytest
from flask import Flask
from flask.ctx import after_this_request
from flask.globals import _cv_app

class TestAfterThisRequest:
    def test_after_this_request_success(self):
        """Test that after_this_request works correctly within a request context."""
        app = Flask(__name__)
        
        with app.test_request_context('/'):
            @after_this_request
            def add_header(response):
                response.headers['X-Test'] = 'TestValue'
                return response
            
            # Verify the function was added to the context
            ctx = _cv_app.get(None)
            assert ctx is not None
            assert ctx.has_request
            assert add_header in ctx._after_request_functions

    def test_after_this_request_no_request_context(self):
        """Test that after_this_request raises RuntimeError when no request context is active."""
        with pytest.raises(RuntimeError) as exc_info:
            @after_this_request
            def add_header(response):
                return response
        
        assert "'after_this_request' can only be used when a request context is active" in str(exc_info.value)

    def test_after_this_request_app_context_only(self):
        """Test that after_this_request raises RuntimeError when only app context is active."""
        app = Flask(__name__)
        
        with app.app_context():
            with pytest.raises(RuntimeError) as exc_info:
                @after_this_request
                def add_header(response):
                    return response
            
            assert "'after_this_request' can only be used when a request context is active" in str(exc_info.value)
