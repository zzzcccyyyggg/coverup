# file: src/flask/src/flask/app.py:473-499
# asked: {"lines": [473, 489, 490, 491, 492, 493, 495, 497, 499], "branches": [[489, 495], [489, 497]]}
# gained: {"lines": [473, 489, 490, 491, 492, 493, 495, 497, 499], "branches": [[489, 495], [489, 497]]}

import pytest
from werkzeug.routing import RequestRedirect
from flask import Flask
from flask.wrappers import Request
from flask.debughelpers import FormDataRoutingRedirect


class TestFlaskRaiseRoutingException:
    """Test cases for Flask.raise_routing_exception method."""
    
    def test_raise_routing_exception_non_debug_mode(self):
        """Test that routing exception is raised directly when not in debug mode."""
        app = Flask(__name__)
        app.debug = False
        
        # Create a mock request with routing exception
        mock_request = Request.from_values()
        mock_routing_exception = RequestRedirect("http://example.com")
        mock_request.routing_exception = mock_routing_exception
        
        # Should raise the routing exception directly
        with pytest.raises(RequestRedirect) as exc_info:
            app.raise_routing_exception(mock_request)
        
        assert exc_info.value is mock_routing_exception
    
    def test_raise_routing_exception_non_redirect_exception(self):
        """Test that non-RequestRedirect exceptions are raised directly."""
        app = Flask(__name__)
        app.debug = True
        
        # Create a mock request with non-redirect routing exception
        mock_request = Request.from_values()
        mock_routing_exception = ValueError("Some error")
        mock_request.routing_exception = mock_routing_exception
        
        # Should raise the routing exception directly
        with pytest.raises(ValueError) as exc_info:
            app.raise_routing_exception(mock_request)
        
        assert exc_info.value is mock_routing_exception
    
    def test_raise_routing_exception_307_308_redirect(self):
        """Test that 307 and 308 redirects are raised directly even in debug mode."""
        app = Flask(__name__)
        app.debug = True
        
        # Test with 307 redirect
        mock_request = Request.from_values(method="POST")
        mock_routing_exception = RequestRedirect("http://example.com")
        mock_routing_exception.code = 307
        mock_request.routing_exception = mock_routing_exception
        
        with pytest.raises(RequestRedirect) as exc_info:
            app.raise_routing_exception(mock_request)
        
        assert exc_info.value is mock_routing_exception
        assert exc_info.value.code == 307
        
        # Test with 308 redirect
        mock_request = Request.from_values(method="POST")
        mock_routing_exception = RequestRedirect("http://example.com")
        mock_routing_exception.code = 308
        mock_request.routing_exception = mock_routing_exception
        
        with pytest.raises(RequestRedirect) as exc_info:
            app.raise_routing_exception(mock_request)
        
        assert exc_info.value is mock_routing_exception
        assert exc_info.value.code == 308
    
    def test_raise_routing_exception_safe_methods(self):
        """Test that GET, HEAD, OPTIONS methods raise routing exception directly."""
        app = Flask(__name__)
        app.debug = True
        
        # Test with GET method
        mock_request = Request.from_values(method="GET")
        mock_routing_exception = RequestRedirect("http://example.com")
        mock_routing_exception.code = 301  # Not 307 or 308
        mock_request.routing_exception = mock_routing_exception
        
        with pytest.raises(RequestRedirect) as exc_info:
            app.raise_routing_exception(mock_request)
        
        assert exc_info.value is mock_routing_exception
        
        # Test with HEAD method
        mock_request = Request.from_values(method="HEAD")
        mock_request.routing_exception = mock_routing_exception
        
        with pytest.raises(RequestRedirect) as exc_info:
            app.raise_routing_exception(mock_request)
        
        assert exc_info.value is mock_routing_exception
        
        # Test with OPTIONS method
        mock_request = Request.from_values(method="OPTIONS")
        mock_request.routing_exception = mock_routing_exception
        
        with pytest.raises(RequestRedirect) as exc_info:
            app.raise_routing_exception(mock_request)
        
        assert exc_info.value is mock_routing_exception
    
    def test_raise_routing_exception_form_data_routing_redirect(self):
        """Test that FormDataRoutingRedirect is raised for unsafe methods in debug mode."""
        app = Flask(__name__)
        app.debug = True
        
        # Create a mock request with unsafe method and redirect
        mock_request = Request.from_values(method="POST")
        mock_routing_exception = RequestRedirect("http://example.com")
        mock_routing_exception.code = 301  # Not 307 or 308
        mock_request.routing_exception = mock_routing_exception
        
        # Should raise FormDataRoutingRedirect
        with pytest.raises(FormDataRoutingRedirect) as exc_info:
            app.raise_routing_exception(mock_request)
        
        # Verify the exception message contains expected information
        assert "A request was sent to" in str(exc_info.value)
        assert "routing issued a redirect" in str(exc_info.value)
        assert "debug mode" in str(exc_info.value)
