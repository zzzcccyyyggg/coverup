# file: src/flask/src/flask/app.py:999-1119
# asked: {"lines": [1064, 1077], "branches": [[1063, 1064], [1076, 1077]]}
# gained: {"lines": [1064, 1077], "branches": [[1063, 1064], [1076, 1077]]}

import pytest
from flask import Flask
from werkzeug.routing import BuildError


class TestFlaskUrlForCoverage:
    """Test cases to cover missing lines in Flask.url_for method."""
    
    def test_url_for_with_blueprint_and_dot_endpoint(self):
        """Test line 1064: endpoint = f"{blueprint_name}{endpoint}" when endpoint starts with '.' and blueprint_name is not None."""
        app = Flask(__name__)
        
        # Create a blueprint and register it with a route
        from flask import Blueprint
        bp = Blueprint('test_bp', __name__)
        
        @bp.route('/test')
        def test_view():
            return "test"
        
        app.register_blueprint(bp)
        
        # Create a request context for the blueprint route
        # This will naturally set the blueprint name in the request context
        with app.test_request_context('/test'):
            # The blueprint should be set to 'test_bp' when accessing a blueprint route
            # Now test url_for with a relative endpoint
            # This should trigger line 1064: endpoint = f"{blueprint_name}{endpoint}"
            # The endpoint will be transformed from '.test_view' to 'test_bp.test_view'
            result = app.url_for('.test_view')
            assert result == '/test'
    
    def test_url_for_with_app_context_but_no_request(self):
        """Test line 1077: url_adapter = ctx.url_adapter when ctx exists but has no request."""
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.com'
        
        # Add a route so we can test URL generation
        @app.route('/test')
        def test_view():
            return "test"
        
        # Push an app context without a request
        with app.app_context():
            # This should use ctx.url_adapter (line 1077)
            # When outside a request context but with app context, URLs are external by default
            result = app.url_for('test_view')
            assert result == 'http://example.com/test'
    
    def test_url_for_with_blueprint_dot_endpoint_no_blueprint(self):
        """Test the else branch when endpoint starts with '.' but blueprint_name is None."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_view():
            return "test"
        
        # Create a request context for a non-blueprint route
        with app.test_request_context('/test'):
            # The blueprint should be None for non-blueprint routes
            # Call url_for with a relative endpoint starting with '.'
            # This should remove the leading dot (endpoint[1:])
            result = app.url_for('.test_view')
            assert result == '/test'
    
    def test_url_for_direct_call_no_context(self):
        """Test the else branch when ctx is None (line 1079)."""
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.com'
        
        @app.route('/test')
        def test_view():
            return "test"
        
        # Call url_for directly without any context
        # This should create a new URL adapter (line 1079)
        # When no context exists, URLs are external by default
        result = app.url_for('test_view')
        assert result == 'http://example.com/test'
    
    def test_url_for_no_adapter_available(self):
        """Test the case where url_adapter is None raises RuntimeError."""
        app = Flask(__name__)
        # Don't set SERVER_NAME
        
        @app.route('/test')
        def test_view():
            return "test"
        
        # Call url_for without SERVER_NAME configured
        with pytest.raises(RuntimeError) as exc_info:
            app.url_for('test_view')
        
        assert "Unable to build URLs outside an active request without 'SERVER_NAME' configured" in str(exc_info.value)
    
    def test_url_for_with_external_false_in_request_context(self):
        """Test that _external=False works correctly in request context."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_view():
            return "test"
        
        with app.test_request_context('/test'):
            # Test with _external=False explicitly set
            result = app.url_for('test_view', _external=False)
            assert result == '/test'
    
    def test_url_for_with_scheme_but_not_external(self):
        """Test that _scheme with _external=False raises ValueError."""
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.com'
        
        @app.route('/test')
        def test_view():
            return "test"
        
        with pytest.raises(ValueError) as exc_info:
            app.url_for('test_view', _scheme='https', _external=False)
        
        assert "When specifying '_scheme', '_external' must be True" in str(exc_info.value)
    
    def test_url_for_with_unknown_endpoint_in_request_context(self):
        """Test BuildError handling for unknown endpoint in request context."""
        app = Flask(__name__)
        
        with app.test_request_context('/'):
            # This should raise BuildError for unknown endpoint
            with pytest.raises(BuildError) as exc_info:
                app.url_for('unknown_endpoint')
            assert 'unknown_endpoint' in str(exc_info.value)
    
    def test_url_for_with_unknown_endpoint_no_context(self):
        """Test BuildError handling for unknown endpoint without context."""
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.com'
        
        # This should raise BuildError for unknown endpoint
        with pytest.raises(BuildError) as exc_info:
            app.url_for('unknown_endpoint')
        assert 'unknown_endpoint' in str(exc_info.value)
