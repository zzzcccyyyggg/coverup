# file: src/flask/src/flask/ctx.py:153-205
# asked: {"lines": [153, 191, 193, 194, 195, 199, 201, 202, 203, 205], "branches": [[193, 194], [193, 199]]}
# gained: {"lines": [153, 191, 193, 194, 195, 199, 201, 202, 203, 205], "branches": [[193, 194], [193, 199]]}

import pytest
from flask import Flask, copy_current_request_context
from flask.ctx import RequestContext
from flask.globals import _cv_app

def test_copy_current_request_context_no_active_context():
    """Test that copy_current_request_context raises RuntimeError when no request context is active."""
    def test_func():
        return "test"
    
    with pytest.raises(RuntimeError) as exc_info:
        copy_current_request_context(test_func)
    
    assert "'copy_current_request_context' can only be used when a request context is active" in str(exc_info.value)

def test_copy_current_request_context_with_active_context():
    """Test that copy_current_request_context works correctly when a request context is active."""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "hello"
    
    with app.test_request_context('/'):
        # Get the current request context
        original_ctx = _cv_app.get(None)
        assert original_ctx is not None
        
        # Test function to be decorated
        def test_func(x, y=0):
            from flask import request
            return f"result: {x + y} - path: {request.path}"
        
        # Apply the decorator
        decorated_func = copy_current_request_context(test_func)
        
        # Verify the wrapper function works correctly
        result = decorated_func(5, y=3)
        assert result == "result: 8 - path: /"
        
        # Verify the wrapper has proper metadata
        assert decorated_func.__name__ == test_func.__name__
        assert decorated_func.__doc__ == test_func.__doc__
        
        # Verify the context was copied (not the same object)
        assert decorated_func.__closure__ is not None
        closure_vars = [cell.cell_contents for cell in decorated_func.__closure__]
        assert len(closure_vars) >= 2
        assert any(isinstance(var, RequestContext) for var in closure_vars)

def test_copy_current_request_context_with_kwargs():
    """Test that copy_current_request_context works with keyword arguments."""
    app = Flask(__name__)
    
    @app.route('/test')
    def test_route():
        return "test"
    
    with app.test_request_context('/test'):
        def test_func(a, b=10, c=20):
            from flask import request
            return f"a={a}, b={b}, c={c}, path={request.path}"
        
        decorated_func = copy_current_request_context(test_func)
        
        # Test with mixed args and kwargs
        result = decorated_func(1, c=30)
        assert result == "a=1, b=10, c=30, path=/test"
        
        # Test with all kwargs
        result = decorated_func(a=5, b=15, c=25)
        assert result == "a=5, b=15, c=25, path=/test"

def test_copy_current_request_context_preserves_context_state():
    """Test that the copied context preserves the original context state."""
    app = Flask(__name__)
    
    @app.route('/preserve')
    def preserve_route():
        return "preserve"
    
    with app.test_request_context('/preserve') as original_ctx:
        original_request = original_ctx.request
        
        def test_func():
            from flask import request
            # Verify we can access the same request path
            assert request.path == '/preserve'
            # Verify it's a different request object (copied context)
            assert request is not original_request
            return "success"
        
        decorated_func = copy_current_request_context(test_func)
        result = decorated_func()
        assert result == "success"

def test_copy_current_request_context_with_session():
    """Test that copy_current_request_context works with session access."""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    @app.route('/session')
    def session_route():
        from flask import session
        session['test_key'] = 'test_value'
        return "session set"
    
    with app.test_request_context('/session'):
        from flask import session
        session['test_key'] = 'test_value'
        
        def test_func():
            from flask import session, request
            # Verify we can access session and request
            assert session.get('test_key') == 'test_value'
            assert request.path == '/session'
            return "session accessed"
        
        decorated_func = copy_current_request_context(test_func)
        result = decorated_func()
        assert result == "session accessed"

def test_copy_current_request_context_multiple_calls():
    """Test that copy_current_request_context can be called multiple times."""
    app = Flask(__name__)
    
    @app.route('/multi')
    def multi_route():
        return "multi"
    
    with app.test_request_context('/multi'):
        def test_func1():
            from flask import request
            return f"func1: {request.path}"
        
        def test_func2(x):
            from flask import request
            return f"func2: {x} - {request.path}"
        
        decorated_func1 = copy_current_request_context(test_func1)
        decorated_func2 = copy_current_request_context(test_func2)
        
        result1 = decorated_func1()
        result2 = decorated_func2(42)
        
        assert result1 == "func1: /multi"
        assert result2 == "func2: 42 - /multi"
