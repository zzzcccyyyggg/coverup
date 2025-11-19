# file: src/flask/src/flask/wrappers.py:161-178
# asked: {"lines": [161, 162, 173, 175, 176, 178], "branches": [[175, 176], [175, 178]]}
# gained: {"lines": [161, 162, 173, 175, 176, 178], "branches": [[175, 176], [175, 178]]}

import pytest
from flask.wrappers import Request

class TestRequestBlueprint:
    """Test cases for the Request.blueprint property."""
    
    def test_blueprint_with_none_endpoint(self):
        """Test blueprint property when endpoint is None."""
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        request.url_rule = None  # This makes endpoint return None
        
        assert request.blueprint is None
    
    def test_blueprint_with_endpoint_no_dot(self):
        """Test blueprint property when endpoint exists but has no dot."""
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        
        # Create a mock url_rule with an endpoint that has no dot
        class MockRule:
            endpoint = "simple_endpoint"
        
        request.url_rule = MockRule()
        
        assert request.blueprint is None
    
    def test_blueprint_with_blueprint_endpoint(self):
        """Test blueprint property when endpoint contains a dot (blueprint)."""
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        
        # Create a mock url_rule with a blueprint-style endpoint
        class MockRule:
            endpoint = "my_blueprint.my_endpoint"
        
        request.url_rule = MockRule()
        
        assert request.blueprint == "my_blueprint"
    
    def test_blueprint_with_nested_blueprint_endpoint(self):
        """Test blueprint property with nested blueprint endpoint."""
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        
        # Create a mock url_rule with a nested blueprint endpoint
        class MockRule:
            endpoint = "parent.child.grandchild.my_endpoint"
        
        request.url_rule = MockRule()
        
        # Should return everything before the last dot
        assert request.blueprint == "parent.child.grandchild"
