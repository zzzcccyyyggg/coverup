# file: src/flask/src/flask/app.py:420-471
# asked: {"lines": [420, 440, 441, 442, 445, 446, 447, 449, 452, 453, 457, 459, 460, 464, 465, 466, 467, 468, 471], "branches": [[440, 441], [440, 464], [441, 442], [441, 445], [449, 452], [449, 453], [453, 457], [453, 459], [464, 465], [464, 471]]}
# gained: {"lines": [420, 440, 441, 442, 445, 446, 447, 449, 452, 453, 457, 459, 460, 464, 465, 466, 467, 468, 471], "branches": [[440, 441], [440, 464], [441, 442], [441, 445], [449, 452], [449, 453], [453, 457], [464, 465], [464, 471]]}

import pytest
from flask import Flask
from flask.wrappers import Request
from werkzeug.routing import MapAdapter
from werkzeug.test import EnvironBuilder


class TestFlaskCreateUrlAdapter:
    """Test cases for Flask.create_url_adapter method to achieve full coverage."""
    
    def test_create_url_adapter_with_request_and_trusted_hosts(self):
        """Test create_url_adapter with request and TRUSTED_HOSTS config."""
        app = Flask(__name__)
        app.config["TRUSTED_HOSTS"] = ["localhost"]
        
        # Create a mock request
        builder = EnvironBuilder(path="/test")
        environ = builder.get_environ()
        request = Request(environ)
        
        adapter = app.create_url_adapter(request)
        
        assert adapter is not None
        assert isinstance(adapter, MapAdapter)
        assert request.trusted_hosts == ["localhost"]
    
    def test_create_url_adapter_with_request_host_matching(self):
        """Test create_url_adapter with request and host_matching enabled."""
        app = Flask(__name__, host_matching=True, static_host="example.com")
        app.config["SERVER_NAME"] = "example.com"
        
        # Create a mock request with matching host
        builder = EnvironBuilder(path="/test", headers={"Host": "example.com"})
        environ = builder.get_environ()
        request = Request(environ)
        
        adapter = app.create_url_adapter(request)
        
        assert adapter is not None
        assert isinstance(adapter, MapAdapter)
    
    def test_create_url_adapter_with_request_subdomain_matching_disabled(self):
        """Test create_url_adapter with request and subdomain_matching disabled."""
        app = Flask(__name__, subdomain_matching=False)
        app.config["SERVER_NAME"] = "example.com"
        app.url_map.default_subdomain = "www"
        
        # Create a mock request
        builder = EnvironBuilder(path="/test", headers={"Host": "example.com"})
        environ = builder.get_environ()
        request = Request(environ)
        
        adapter = app.create_url_adapter(request)
        
        assert adapter is not None
        assert isinstance(adapter, MapAdapter)
    
    def test_create_url_adapter_with_request_subdomain_matching_disabled_no_default(self):
        """Test create_url_adapter with request, subdomain_matching disabled, no default subdomain."""
        app = Flask(__name__, subdomain_matching=False)
        app.config["SERVER_NAME"] = "example.com"
        # Ensure no default subdomain
        app.url_map.default_subdomain = None
        
        # Create a mock request
        builder = EnvironBuilder(path="/test", headers={"Host": "example.com"})
        environ = builder.get_environ()
        request = Request(environ)
        
        adapter = app.create_url_adapter(request)
        
        assert adapter is not None
        assert isinstance(adapter, MapAdapter)
    
    def test_create_url_adapter_without_request_with_server_name(self):
        """Test create_url_adapter without request but with SERVER_NAME configured."""
        app = Flask(__name__)
        app.config["SERVER_NAME"] = "example.com"
        app.config["APPLICATION_ROOT"] = "/app"
        app.config["PREFERRED_URL_SCHEME"] = "https"
        
        adapter = app.create_url_adapter(None)
        
        assert adapter is not None
        assert isinstance(adapter, MapAdapter)
    
    def test_create_url_adapter_without_request_no_server_name(self):
        """Test create_url_adapter without request and no SERVER_NAME configured."""
        app = Flask(__name__)
        app.config["SERVER_NAME"] = None
        
        adapter = app.create_url_adapter(None)
        
        assert adapter is None
    
    def test_create_url_adapter_with_request_no_trusted_hosts(self):
        """Test create_url_adapter with request but no TRUSTED_HOSTS configured."""
        app = Flask(__name__)
        app.config["TRUSTED_HOSTS"] = None
        
        # Create a mock request
        builder = EnvironBuilder(path="/test")
        environ = builder.get_environ()
        request = Request(environ)
        
        adapter = app.create_url_adapter(request)
        
        assert adapter is not None
        assert isinstance(adapter, MapAdapter)
        # Should not set trusted_hosts when config is None
        assert not hasattr(request, 'trusted_hosts') or request.trusted_hosts is None
