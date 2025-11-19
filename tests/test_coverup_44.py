# file: src/flask/src/flask/sansio/blueprints.py:87-116
# asked: {"lines": [87, 90, 91, 98, 99, 100, 102, 103, 104, 105, 106, 107, 108, 110, 111, 112, 113, 114, 115], "branches": [[98, 99], [98, 103], [99, 100], [99, 102], [104, 105], [104, 106], [107, 108], [107, 110]]}
# gained: {"lines": [87, 90, 91, 98, 99, 100, 102, 103, 104, 105, 106, 107, 108, 110, 111, 112, 113, 114, 115], "branches": [[98, 99], [98, 103], [99, 100], [99, 102], [104, 105], [104, 106], [107, 108], [107, 110]]}

import pytest
from flask.sansio.blueprints import BlueprintSetupState
from flask.sansio.app import App
from flask import typing as ft

class MockApp:
    """Mock App class to avoid initialization issues."""
    def __init__(self):
        self.url_map = MockUrlMap()
        self.name = 'test_app'
    
    def add_url_rule(self, rule, endpoint, view_func, defaults=None, **options):
        self.url_map.add_rule(rule, endpoint, view_func, defaults, options)

class MockUrlMap:
    """Mock URL map to track added rules."""
    def __init__(self):
        self._rules = []
    
    def add_rule(self, rule, endpoint, view_func, defaults, options):
        self._rules.append({
            'rule': rule,
            'endpoint': endpoint,
            'view_func': view_func,
            'defaults': defaults,
            'options': options
        })

def test_add_url_rule_with_url_prefix_and_rule():
    """Test add_url_rule when url_prefix is set and rule is provided."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': '/api', 'url_values_defaults': {}})()
    state = BlueprintSetupState(blueprint, app, {}, True)
    
    def view_func():
        return "test"
    
    state.add_url_rule('/users', view_func=view_func)
    
    # Verify the rule was added with proper prefix
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['rule'] == '/api/users'

def test_add_url_rule_with_url_prefix_empty_rule():
    """Test add_url_rule when url_prefix is set and rule is empty."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': '/api', 'url_values_defaults': {}})()
    state = BlueprintSetupState(blueprint, app, {}, True)
    
    def view_func():
        return "test"
    
    state.add_url_rule('', view_func=view_func)
    
    # Verify the rule was added with just the prefix
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['rule'] == '/api'

def test_add_url_rule_with_subdomain():
    """Test add_url_rule with subdomain option."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': None, 'url_values_defaults': {}})()
    state = BlueprintSetupState(blueprint, app, {'subdomain': 'admin'}, True)
    
    def view_func():
        return "test"
    
    state.add_url_rule('/users', view_func=view_func)
    
    # Verify the rule was added with subdomain
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['options'].get('subdomain') == 'admin'

def test_add_url_rule_with_endpoint_none():
    """Test add_url_rule when endpoint is None (should be derived from view_func)."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': None, 'url_values_defaults': {}})()
    state = BlueprintSetupState(blueprint, app, {}, True)
    
    def my_view_func():
        return "test"
    
    state.add_url_rule('/users', endpoint=None, view_func=my_view_func)
    
    # Verify endpoint was derived from view_func name
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['endpoint'] == 'test_bp.my_view_func'

def test_add_url_rule_with_defaults_override():
    """Test add_url_rule when defaults are provided and overridden."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': None, 'url_values_defaults': {'page': 1}})()
    state = BlueprintSetupState(blueprint, app, {}, True)
    
    def view_func():
        return "test"
    
    state.add_url_rule('/users', view_func=view_func, defaults={'page': 2, 'limit': 10})
    
    # Verify defaults were properly merged
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['defaults'] == {'page': 2, 'limit': 10}

def test_add_url_rule_with_name_prefix():
    """Test add_url_rule with name_prefix option."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': None, 'url_values_defaults': {}})()
    state = BlueprintSetupState(blueprint, app, {'name_prefix': 'v1'}, True)
    
    def view_func():
        return "test"
    
    state.add_url_rule('/users', endpoint='users', view_func=view_func)
    
    # Verify endpoint includes name_prefix
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['endpoint'] == 'v1.test_bp.users'

def test_add_url_rule_without_url_prefix():
    """Test add_url_rule when url_prefix is None."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': None, 'url_values_defaults': {}})()
    state = BlueprintSetupState(blueprint, app, {}, True)
    
    def view_func():
        return "test"
    
    state.add_url_rule('/users', view_func=view_func)
    
    # Verify the rule was added without prefix
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['rule'] == '/users'

def test_add_url_rule_with_custom_endpoint():
    """Test add_url_rule with explicit endpoint."""
    app = MockApp()
    blueprint = type('Blueprint', (), {'name': 'test_bp', 'subdomain': None, 'url_prefix': None, 'url_values_defaults': {}})()
    state = BlueprintSetupState(blueprint, app, {}, True)
    
    def view_func():
        return "test"
    
    state.add_url_rule('/users', endpoint='custom_endpoint', view_func=view_func)
    
    # Verify custom endpoint was used
    assert len(app.url_map._rules) == 1
    rule = app.url_map._rules[0]
    assert rule['endpoint'] == 'test_bp.custom_endpoint'
