# file: src/flask/src/flask/sansio/app.py:953-972
# asked: {"lines": [953, 960, 964, 965, 966, 969, 970, 971, 972], "branches": [[964, 965], [964, 969], [969, 0], [969, 970], [970, 969], [970, 971], [971, 969], [971, 972]]}
# gained: {"lines": [953, 960, 964, 965, 966, 969, 970, 971, 972], "branches": [[964, 965], [964, 969], [969, 0], [969, 970], [970, 969], [970, 971], [971, 969], [971, 972]]}

import pytest
from flask import Flask
from flask.sansio.app import App

class TestAppInjectUrlDefaults:
    """Test cases for App.inject_url_defaults method to achieve full coverage."""
    
    def test_inject_url_defaults_without_blueprint(self):
        """Test inject_url_defaults when endpoint has no blueprint (no '.' in endpoint)."""
        app = Flask(__name__)
        values = {}
        
        # This should execute lines 953-960, 969-972 but skip the blueprint path logic
        app.inject_url_defaults("simple_endpoint", values)
        
        # Verify values dict is unchanged (no URL defaults were registered)
        assert values == {}
    
    def test_inject_url_defaults_with_blueprint_but_no_functions(self):
        """Test inject_url_defaults when endpoint has blueprint but no URL default functions are registered."""
        app = Flask(__name__)
        values = {}
        
        # This should execute the blueprint path logic but no functions are registered
        app.inject_url_defaults("blueprint.some_endpoint", values)
        
        # Verify values dict is unchanged (no URL defaults were registered)
        assert values == {}
    
    def test_inject_url_defaults_with_blueprint_and_functions(self):
        """Test inject_url_defaults when endpoint has blueprint and URL default functions are registered."""
        app = Flask(__name__)
        values = {"existing": "value"}
        called_functions = []
        
        def default_func1(endpoint, vals):
            called_functions.append(("func1", endpoint, vals.copy()))
            vals["default1"] = "value1"
        
        def default_func2(endpoint, vals):
            called_functions.append(("func2", endpoint, vals.copy()))
            vals["default2"] = "value2"
        
        # Register URL default functions for the blueprint
        app.url_default_functions["blueprint"] = [default_func1, default_func2]
        
        # This should execute all lines including the blueprint path logic and function calls
        app.inject_url_defaults("blueprint.some_endpoint", values)
        
        # Verify functions were called with correct parameters
        assert len(called_functions) == 2
        assert called_functions[0] == ("func1", "blueprint.some_endpoint", {"existing": "value"})
        assert called_functions[1] == ("func2", "blueprint.some_endpoint", {"existing": "value", "default1": "value1"})
        
        # Verify values dict was modified by the functions
        assert values == {"existing": "value", "default1": "value1", "default2": "value2"}
    
    def test_inject_url_defaults_with_nested_blueprint(self):
        """Test inject_url_defaults with nested blueprint path (e.g., 'parent.child.endpoint')."""
        app = Flask(__name__)
        values = {}
        called_functions = []
        
        def parent_func(endpoint, vals):
            called_functions.append(("parent", endpoint, vals.copy()))
            vals["parent"] = "parent_value"
        
        def child_func(endpoint, vals):
            called_functions.append(("child", endpoint, vals.copy()))
            vals["child"] = "child_value"
        
        # Register URL default functions for both parent and child blueprints
        app.url_default_functions["parent"] = [parent_func]
        app.url_default_functions["parent.child"] = [child_func]
        
        # This should execute the nested blueprint path logic
        app.inject_url_defaults("parent.child.some_endpoint", values)
        
        # Verify functions were called in correct order
        # For "parent.child.some_endpoint", _split_blueprint_path("parent.child") returns ["parent.child", "parent"]
        # So names will be: [None, "parent", "parent.child"] (reversed order)
        assert len(called_functions) == 2
        # First: parent (parent_func) - the reversed order means parent comes before parent.child
        assert called_functions[0] == ("parent", "parent.child.some_endpoint", {})
        # Then: parent.child (child_func)
        assert called_functions[1] == ("child", "parent.child.some_endpoint", {"parent": "parent_value"})
        
        # Verify values dict was modified by the functions
        assert values == {"parent": "parent_value", "child": "child_value"}
    
    def test_inject_url_defaults_with_global_and_blueprint_functions(self):
        """Test inject_url_defaults with both global (None) and blueprint-specific functions."""
        app = Flask(__name__)
        values = {}
        called_functions = []
        
        def global_func(endpoint, vals):
            called_functions.append(("global", endpoint, vals.copy()))
            vals["global"] = "global_value"
        
        def blueprint_func(endpoint, vals):
            called_functions.append(("blueprint", endpoint, vals.copy()))
            vals["blueprint"] = "blueprint_value"
        
        # Register both global (None) and blueprint-specific functions
        app.url_default_functions[None] = [global_func]
        app.url_default_functions["blueprint"] = [blueprint_func]
        
        # This should execute both global and blueprint functions
        app.inject_url_defaults("blueprint.some_endpoint", values)
        
        # Verify functions were called in correct order (None first, then blueprint)
        assert len(called_functions) == 2
        assert called_functions[0] == ("global", "blueprint.some_endpoint", {})
        assert called_functions[1] == ("blueprint", "blueprint.some_endpoint", {"global": "global_value"})
        
        # Verify values dict was modified by both functions
        assert values == {"global": "global_value", "blueprint": "blueprint_value"}
