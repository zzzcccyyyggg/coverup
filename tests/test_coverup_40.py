# file: src/flask/src/flask/debughelpers.py:50-78
# asked: {"lines": [50, 51, 57, 58, 59, 60, 61, 62, 65, 66, 67, 72, 73, 78], "branches": [[65, 66], [65, 72]]}
# gained: {"lines": [50, 51, 57, 58, 59, 60, 61, 62, 65, 66, 67, 72, 73, 78], "branches": [[65, 66], [65, 72]]}

import pytest
from werkzeug.routing import RequestRedirect
from flask.wrappers import Request
from flask.debughelpers import FormDataRoutingRedirect

class MockRequestRedirect(RequestRedirect):
    def __init__(self, new_url):
        self.new_url = new_url

class TestFormDataRoutingRedirect:
    def test_init_with_trailing_slash_redirect(self):
        """Test FormDataRoutingRedirect initialization when redirect adds trailing slash"""
        mock_request = Request({'REQUEST_METHOD': 'POST', 'wsgi.url_scheme': 'http', 'SERVER_NAME': 'localhost', 'SERVER_PORT': '5000', 'PATH_INFO': '/test'})
        mock_request.url = 'http://localhost:5000/test'
        mock_request.base_url = 'http://localhost:5000/test'
        mock_request.routing_exception = MockRequestRedirect('http://localhost:5000/test/')
        
        with pytest.raises(FormDataRoutingRedirect) as exc_info:
            raise FormDataRoutingRedirect(mock_request)
        
        error_msg = str(exc_info.value)
        assert "A request was sent to 'http://localhost:5000/test', but routing issued a redirect to the canonical URL 'http://localhost:5000/test/'." in error_msg
        assert "The URL was defined with a trailing slash." in error_msg
        assert "Send requests to the canonical URL, or use 307 or 308 for routing redirects." in error_msg

    def test_init_without_trailing_slash_redirect(self):
        """Test FormDataRoutingRedirect initialization when redirect doesn't add trailing slash"""
        mock_request = Request({'REQUEST_METHOD': 'POST', 'wsgi.url_scheme': 'http', 'SERVER_NAME': 'localhost', 'SERVER_PORT': '5000', 'PATH_INFO': '/test'})
        mock_request.url = 'http://localhost:5000/test'
        mock_request.base_url = 'http://localhost:5000/test'
        mock_request.routing_exception = MockRequestRedirect('http://localhost:5000/other')
        
        with pytest.raises(FormDataRoutingRedirect) as exc_info:
            raise FormDataRoutingRedirect(mock_request)
        
        error_msg = str(exc_info.value)
        assert "A request was sent to 'http://localhost:5000/test', but routing issued a redirect to the canonical URL 'http://localhost:5000/other'." in error_msg
        assert "The URL was defined with a trailing slash." not in error_msg
        assert "Send requests to the canonical URL, or use 307 or 308 for routing redirects." in error_msg

    def test_init_with_query_params(self):
        """Test FormDataRoutingRedirect initialization with query parameters in redirect URL"""
        mock_request = Request({'REQUEST_METHOD': 'POST', 'wsgi.url_scheme': 'http', 'SERVER_NAME': 'localhost', 'SERVER_PORT': '5000', 'PATH_INFO': '/test'})
        mock_request.url = 'http://localhost:5000/test'
        mock_request.base_url = 'http://localhost:5000/test'
        mock_request.routing_exception = MockRequestRedirect('http://localhost:5000/test/?param=value')
        
        with pytest.raises(FormDataRoutingRedirect) as exc_info:
            raise FormDataRoutingRedirect(mock_request)
        
        error_msg = str(exc_info.value)
        assert "A request was sent to 'http://localhost:5000/test', but routing issued a redirect to the canonical URL 'http://localhost:5000/test/?param=value'." in error_msg
        assert "The URL was defined with a trailing slash." in error_msg
        assert "Send requests to the canonical URL, or use 307 or 308 for routing redirects." in error_msg
