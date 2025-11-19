# file: src/flask/src/flask/app.py:999-1119
# asked: {"lines": [999, 1004, 1005, 1006, 1007, 1056, 1057, 1058, 1062, 1063, 1064, 1066, 1070, 1071, 1076, 1077, 1079, 1081, 1082, 1083, 1091, 1092, 1096, 1097, 1099, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1109, 1110, 1111, 1113, 1115, 1116, 1117, 1119], "branches": [[1056, 1057], [1056, 1076], [1062, 1063], [1062, 1070], [1063, 1064], [1063, 1066], [1070, 1071], [1070, 1096], [1076, 1077], [1076, 1079], [1081, 1082], [1081, 1091], [1091, 1092], [1091, 1096], [1096, 1097], [1096, 1099], [1115, 1116], [1115, 1119]]}
# gained: {"lines": [999, 1004, 1005, 1006, 1007, 1056, 1057, 1058, 1062, 1063, 1066, 1070, 1071, 1076, 1079, 1081, 1082, 1083, 1091, 1092, 1096, 1097, 1099, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1109, 1110, 1111, 1113, 1115, 1116, 1117, 1119], "branches": [[1056, 1057], [1056, 1076], [1062, 1063], [1062, 1070], [1063, 1066], [1070, 1071], [1070, 1096], [1076, 1079], [1081, 1082], [1081, 1091], [1091, 1092], [1091, 1096], [1096, 1097], [1096, 1099], [1115, 1116], [1115, 1119]]}

import pytest
from flask import Flask
from werkzeug.routing import BuildError


class TestFlaskUrlFor:
    """Test cases for Flask.url_for method to achieve full coverage."""

    def test_url_for_with_anchor(self):
        """Test url_for with _anchor parameter."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        with app.test_request_context():
            url = app.url_for('test_endpoint', _anchor='section1')
            assert url == '/test#section1'

    def test_url_for_with_method(self):
        """Test url_for with _method parameter."""
        app = Flask(__name__)
        
        @app.route('/test', methods=['GET', 'POST'])
        def test_endpoint():
            return "test"
        
        with app.test_request_context():
            url = app.url_for('test_endpoint', _method='POST')
            assert url == '/test'

    def test_url_for_with_scheme_and_external_false_raises_error(self):
        """Test that _scheme with _external=False raises ValueError."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        with app.test_request_context():
            with pytest.raises(ValueError, match="When specifying '_scheme', '_external' must be True"):
                app.url_for('test_endpoint', _scheme='https', _external=False)

    def test_url_for_build_error_handled(self):
        """Test BuildError handling in url_for."""
        app = Flask(__name__)
        
        # Mock handle_url_build_error to return a string instead of raising
        def mock_handler(error, endpoint, values):
            return "/fallback"
        
        app.handle_url_build_error = mock_handler
        
        with app.test_request_context():
            # Try to build URL for non-existent endpoint
            url = app.url_for('nonexistent_endpoint')
            assert url == "/fallback"

    def test_url_for_outside_request_without_server_name_raises_error(self):
        """Test url_for outside request context without SERVER_NAME raises RuntimeError."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        # No request context, no SERVER_NAME configured
        with pytest.raises(RuntimeError, match="Unable to build URLs outside an active request"):
            app.url_for('test_endpoint')

    def test_url_for_outside_request_with_server_name(self):
        """Test url_for outside request context with SERVER_NAME configured."""
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.com'
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        # No request context, but SERVER_NAME is configured
        url = app.url_for('test_endpoint')
        assert url == 'http://example.com/test'

    def test_url_for_with_blueprint_relative_endpoint(self):
        """Test url_for with relative blueprint endpoint (starts with .)."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        with app.test_request_context():
            # Test relative endpoint without blueprint context
            url = app.url_for('.test_endpoint')
            assert url == '/test'

    def test_url_for_with_external_and_scheme(self):
        """Test url_for with _external=True and _scheme."""
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.com'
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        # Outside request context
        url = app.url_for('test_endpoint', _external=True, _scheme='https')
        assert url == 'https://example.com/test'

    def test_url_for_with_values_as_query_params(self):
        """Test url_for with additional values that become query parameters."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        with app.test_request_context():
            url = app.url_for('test_endpoint', param1='value1', param2='value2')
            assert url == '/test?param1=value1&param2=value2'

    def test_url_for_anchor_encoding(self):
        """Test that _anchor is properly URL encoded."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        with app.test_request_context():
            url = app.url_for('test_endpoint', _anchor='section with spaces')
            assert url == '/test#section%20with%20spaces'

    def test_url_for_in_request_context_external_default_false(self):
        """Test that in request context, _external defaults to False unless _scheme is given."""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        with app.test_request_context():
            # Without _scheme, _external should default to False
            url = app.url_for('test_endpoint')
            assert url == '/test'
            
            # With _scheme, _external should default to True
            url_with_scheme = app.url_for('test_endpoint', _scheme='https')
            assert url_with_scheme == 'https://localhost/test'

    def test_url_for_outside_request_context_external_default_true(self):
        """Test that outside request context, _external defaults to True."""
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.com'
        
        @app.route('/test')
        def test_endpoint():
            return "test"
        
        # Outside request context, _external should default to True
        url = app.url_for('test_endpoint')
        assert url == 'http://example.com/test'

    def test_url_for_with_url_defaults(self):
        """Test that url_defaults are injected."""
        app = Flask(__name__)
        
        @app.route('/test/<value>')
        def test_endpoint(value):
            return f"test {value}"
        
        # Add a URL default function
        def inject_default(endpoint, values):
            if endpoint == 'test_endpoint' and 'value' not in values:
                values['value'] = 'default'
        
        app.url_default_functions[None] = [inject_default]
        
        with app.test_request_context():
            url = app.url_for('test_endpoint')
            assert url == '/test/default'

    def test_url_for_build_error_re_raised_when_no_handler(self):
        """Test that BuildError is re-raised when no handler returns a value."""
        app = Flask(__name__)
        
        with app.test_request_context():
            with pytest.raises(BuildError):
                app.url_for('nonexistent_endpoint')
