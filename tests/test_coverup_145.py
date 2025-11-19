# file: src/flask/src/flask/app.py:1396-1443
# asked: {"lines": [1396, 1434, 1436, 1438, 1439, 1441, 1443], "branches": []}
# gained: {"lines": [1396, 1434, 1436, 1438, 1439, 1441, 1443], "branches": []}

import pytest
from flask import Flask
from flask.ctx import AppContext


def test_test_request_context_basic():
    """Test basic test_request_context functionality."""
    app = Flask(__name__)
    
    with app.test_request_context('/test') as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/test'
        assert ctx.app is app


def test_test_request_context_with_json():
    """Test test_request_context with JSON data."""
    app = Flask(__name__)
    
    with app.test_request_context('/api', json={'key': 'value'}) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/api'
        assert ctx.request.json == {'key': 'value'}
        assert ctx.request.content_type == 'application/json'


def test_test_request_context_with_form_data():
    """Test test_request_context with form data."""
    app = Flask(__name__)
    
    with app.test_request_context('/submit', data={'field': 'value'}) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/submit'
        assert ctx.request.form['field'] == 'value'


def test_test_request_context_with_query_string():
    """Test test_request_context with query string parameters."""
    app = Flask(__name__)
    
    with app.test_request_context('/search?q=flask') as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/search'
        assert ctx.request.args['q'] == 'flask'


def test_test_request_context_with_custom_headers():
    """Test test_request_context with custom headers."""
    app = Flask(__name__)
    
    with app.test_request_context(
        '/protected',
        headers={'Authorization': 'Bearer token123'}
    ) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/protected'
        assert ctx.request.headers['Authorization'] == 'Bearer token123'


def test_test_request_context_with_method():
    """Test test_request_context with specific HTTP method."""
    app = Flask(__name__)
    
    with app.test_request_context('/delete', method='DELETE') as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/delete'
        assert ctx.request.method == 'DELETE'


def test_test_request_context_with_base_url():
    """Test test_request_context with custom base_url."""
    app = Flask(__name__)
    
    with app.test_request_context(
        '/path',
        base_url='https://example.com'
    ) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/path'
        assert ctx.request.host == 'example.com'
        assert ctx.request.scheme == 'https'


def test_test_request_context_with_subdomain():
    """Test test_request_context with subdomain."""
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    
    with app.test_request_context(
        '/admin',
        subdomain='api'
    ) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/admin'
        assert ctx.request.host == 'api.example.com'


def test_test_request_context_with_url_scheme():
    """Test test_request_context with custom URL scheme."""
    app = Flask(__name__)
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    
    with app.test_request_context(
        '/secure',
        url_scheme='http'
    ) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/secure'
        assert ctx.request.scheme == 'http'


def test_test_request_context_multiple_args():
    """Test test_request_context with multiple positional arguments."""
    app = Flask(__name__)
    
    # This tests that *args are properly passed to EnvironBuilder
    with app.test_request_context('/test', 'GET') as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/test'
        assert ctx.request.method == 'GET'


def test_test_request_context_complex_scenario():
    """Test test_request_context with complex combination of parameters."""
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'test.com'
    app.config['APPLICATION_ROOT'] = '/app'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    
    with app.test_request_context(
        '/api/users',
        method='POST',
        json={'name': 'test'},
        headers={'Content-Type': 'application/json', 'X-Custom': 'value'},
        subdomain='api'
    ) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.request.path == '/api/users'
        assert ctx.request.method == 'POST'
        assert ctx.request.json == {'name': 'test'}
        assert ctx.request.headers['X-Custom'] == 'value'
        assert ctx.request.host == 'api.test.com'
