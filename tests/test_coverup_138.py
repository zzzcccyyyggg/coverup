# file: src/flask/src/flask/wrappers.py:146-159
# asked: {"lines": [146, 147, 156, 157, 159], "branches": [[156, 157], [156, 159]]}
# gained: {"lines": [146, 147, 156, 157, 159], "branches": [[156, 157], [156, 159]]}

import pytest
from werkzeug.routing import Rule
from flask.wrappers import Request


class TestRequestEndpoint:
    """Test cases for the Request.endpoint property."""

    def test_endpoint_with_url_rule(self):
        """Test endpoint property when url_rule is set with an endpoint."""
        # Create a mock Rule with an endpoint
        rule = Rule('/test', endpoint='test_endpoint')
        
        # Create a Request instance and set the url_rule
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/test'})
        request.url_rule = rule
        
        # Assert that endpoint returns the rule's endpoint
        assert request.endpoint == 'test_endpoint'

    def test_endpoint_without_url_rule(self):
        """Test endpoint property when url_rule is None."""
        # Create a Request instance without setting url_rule
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/test'})
        
        # Assert that endpoint returns None when url_rule is None
        assert request.endpoint is None

    def test_endpoint_with_url_rule_none_endpoint(self):
        """Test endpoint property when url_rule exists but endpoint is None."""
        # Create a Rule with endpoint explicitly set to None
        rule = Rule('/test', endpoint=None)
        
        # Create a Request instance and set the url_rule
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/test'})
        request.url_rule = rule
        
        # Assert that endpoint returns None when url_rule.endpoint is None
        assert request.endpoint is None
