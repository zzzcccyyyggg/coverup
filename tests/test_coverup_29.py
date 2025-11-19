# file: src/flask/src/flask/testing.py:49-86
# asked: {"lines": [49, 52, 53, 54, 55, 59, 60, 61, 62, 65, 66, 67, 69, 70, 72, 73, 75, 76, 77, 78, 80, 82, 83, 85, 86], "branches": [[65, 66], [65, 85], [69, 70], [69, 72], [72, 73], [72, 75], [82, 83], [82, 85]]}
# gained: {"lines": [49, 52, 53, 54, 55, 59, 60, 61, 62, 65, 66, 67, 69, 70, 72, 73, 75, 76, 77, 78, 80, 82, 83, 85, 86], "branches": [[65, 66], [65, 85], [69, 70], [69, 72], [72, 73], [72, 75], [82, 83], [82, 85]]}

import pytest
from flask import Flask
from flask.testing import EnvironBuilder


def test_environbuilder_with_base_url_and_subdomain_raises_assertion():
    """Test that passing base_url with subdomain raises AssertionError."""
    app = Flask(__name__)
    
    with pytest.raises(AssertionError, match='Cannot pass "subdomain" or "url_scheme" with "base_url"'):
        EnvironBuilder(app, base_url="http://example.com", subdomain="api")


def test_environbuilder_with_base_url_and_url_scheme_raises_assertion():
    """Test that passing base_url with url_scheme raises AssertionError."""
    app = Flask(__name__)
    
    with pytest.raises(AssertionError, match='Cannot pass "subdomain" or "url_scheme" with "base_url"'):
        EnvironBuilder(app, base_url="http://example.com", url_scheme="https")


def test_environbuilder_with_subdomain_and_no_server_name():
    """Test EnvironBuilder with subdomain when SERVER_NAME is not configured."""
    app = Flask(__name__)
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    builder = EnvironBuilder(app, subdomain='api')
    assert builder.app is app
    assert 'api.localhost' in builder.base_url


def test_environbuilder_with_subdomain_and_server_name():
    """Test EnvironBuilder with subdomain when SERVER_NAME is configured."""
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    builder = EnvironBuilder(app, subdomain='api')
    assert builder.app is app
    assert 'api.example.com' in builder.base_url


def test_environbuilder_with_custom_url_scheme():
    """Test EnvironBuilder with custom url_scheme parameter."""
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    builder = EnvironBuilder(app, url_scheme='https')
    assert builder.app is app
    assert builder.base_url.startswith('https://')


def test_environbuilder_with_path_containing_scheme_and_netloc():
    """Test EnvironBuilder with path containing scheme and netloc."""
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    builder = EnvironBuilder(app, path='https://custom.com/path')
    assert builder.app is app
    assert builder.base_url == 'https://custom.com/'


def test_environbuilder_with_path_containing_query():
    """Test EnvironBuilder with path containing query string."""
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    builder = EnvironBuilder(app, path='/path?param=value')
    assert builder.app is app
    # The query string should be preserved in the path when base_url is None
    assert builder.path == '/path'
    # Check that query string is handled separately in werkzeug's EnvironBuilder
    assert hasattr(builder, 'query_string')
    assert builder.query_string == 'param=value'


def test_environbuilder_with_application_root():
    """Test EnvironBuilder with non-root APPLICATION_ROOT."""
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    app.config['APPLICATION_ROOT'] = '/app'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    builder = EnvironBuilder(app)
    assert builder.app is app
    # werkzeug's EnvironBuilder adds trailing slash to base_url
    assert builder.base_url == 'http://example.com/app/'


def test_environbuilder_with_base_url_provided():
    """Test EnvironBuilder when base_url is explicitly provided."""
    app = Flask(__name__)
    
    builder = EnvironBuilder(app, base_url='https://api.example.com/v1')
    assert builder.app is app
    # werkzeug's EnvironBuilder adds trailing slash to base_url
    assert builder.base_url == 'https://api.example.com/v1/'
