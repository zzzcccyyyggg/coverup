# file: src/flask/src/flask/sansio/scaffold.py:367-433
# asked: {"lines": [367, 368, 371, 372, 373, 433], "branches": []}
# gained: {"lines": [367, 368, 371, 372, 373], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffoldAddUrlRule:
    """Test cases for Scaffold.add_url_rule method to achieve full coverage."""
    
    def test_add_url_rule_not_implemented(self):
        """Test that add_url_rule raises NotImplementedError."""
        scaffold = Scaffold("test_app")
        with pytest.raises(NotImplementedError):
            scaffold.add_url_rule("/test")
    
    def test_add_url_rule_with_all_parameters(self):
        """Test add_url_rule with all parameters provided."""
        scaffold = Scaffold("test_app")
        
        def dummy_view():
            return "dummy"
        
        with pytest.raises(NotImplementedError):
            scaffold.add_url_rule(
                rule="/test",
                endpoint="test_endpoint",
                view_func=dummy_view,
                provide_automatic_options=True,
                methods=["GET", "POST"]
            )
    
    def test_add_url_rule_with_minimal_parameters(self):
        """Test add_url_rule with minimal parameters."""
        scaffold = Scaffold("test_app")
        
        with pytest.raises(NotImplementedError):
            scaffold.add_url_rule("/minimal")
    
    def test_add_url_rule_with_view_func_only(self):
        """Test add_url_rule with view_func parameter only."""
        scaffold = Scaffold("test_app")
        
        def view_func():
            return "test"
        
        with pytest.raises(NotImplementedError):
            scaffold.add_url_rule("/test", view_func=view_func)
    
    def test_add_url_rule_with_endpoint_only(self):
        """Test add_url_rule with endpoint parameter only."""
        scaffold = Scaffold("test_app")
        
        with pytest.raises(NotImplementedError):
            scaffold.add_url_rule("/test", endpoint="custom_endpoint")
    
    def test_add_url_rule_with_options(self):
        """Test add_url_rule with additional options."""
        scaffold = Scaffold("test_app")
        
        with pytest.raises(NotImplementedError):
            scaffold.add_url_rule(
                "/test", 
                endpoint="test",
                defaults={"page": 1},
                subdomain="api"
            )
