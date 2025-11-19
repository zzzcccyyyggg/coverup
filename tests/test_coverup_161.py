# file: src/flask/src/flask/wrappers.py:180-195
# asked: {"lines": [180, 181, 190, 192, 193, 195], "branches": [[192, 193], [192, 195]]}
# gained: {"lines": [180, 181, 190, 192, 193, 195], "branches": [[192, 193], [192, 195]]}

import pytest
from flask.wrappers import Request
from werkzeug.test import EnvironBuilder
from werkzeug.routing import Rule


class TestRequestBlueprints:
    """Test cases for Request.blueprints property."""

    def test_blueprints_when_blueprint_is_none(self):
        """Test blueprints property returns empty list when blueprint is None."""
        builder = EnvironBuilder()
        environ = builder.get_environ()
        request = Request(environ)
        
        # When url_rule is None, endpoint should be None, blueprint should be None
        assert request.url_rule is None
        assert request.endpoint is None
        assert request.blueprint is None
        
        # Test that blueprints returns empty list
        result = request.blueprints
        assert result == []
        assert isinstance(result, list)

    def test_blueprints_when_blueprint_is_simple_name(self):
        """Test blueprints property with a simple blueprint name."""
        builder = EnvironBuilder()
        environ = builder.get_environ()
        request = Request(environ)
        
        # Set url_rule with endpoint that triggers a simple blueprint
        request.url_rule = Rule("/test", endpoint="simple_blueprint.view")
        
        # Test that blueprints returns the split path
        result = request.blueprints
        assert result == ["simple_blueprint"]
        assert isinstance(result, list)

    def test_blueprints_when_blueprint_has_dots(self):
        """Test blueprints property with a nested blueprint path."""
        builder = EnvironBuilder()
        environ = builder.get_environ()
        request = Request(environ)
        
        # Set url_rule with endpoint that triggers a nested blueprint path
        request.url_rule = Rule("/test", endpoint="parent.child.grandchild.view")
        
        # Test that blueprints returns the split path
        result = request.blueprints
        assert result == ["parent.child.grandchild", "parent.child", "parent"]
        assert isinstance(result, list)

    def test_blueprints_when_endpoint_has_no_dot(self):
        """Test blueprints property when endpoint has no dot (no blueprint)."""
        builder = EnvironBuilder()
        environ = builder.get_environ()
        request = Request(environ)
        
        # Set url_rule with endpoint that has no dot (no blueprint)
        request.url_rule = Rule("/test", endpoint="view_function")
        
        # When endpoint has no dot, blueprint should be None
        assert request.blueprint is None
        
        # Test that blueprints returns empty list
        result = request.blueprints
        assert result == []
        assert isinstance(result, list)

    def test_blueprints_when_endpoint_is_nested_single_level(self):
        """Test blueprints property with single-level blueprint."""
        builder = EnvironBuilder()
        environ = builder.get_environ()
        request = Request(environ)
        
        # Set url_rule with endpoint with single-level blueprint
        request.url_rule = Rule("/test", endpoint="blueprint.view")
        
        # Test that blueprints returns the split path
        result = request.blueprints
        assert result == ["blueprint"]
        assert isinstance(result, list)
