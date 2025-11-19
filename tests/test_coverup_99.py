# file: src/flask/src/flask/sansio/blueprints.py:41-85
# asked: {"lines": [41, 49, 52, 56, 62, 64, 65, 66, 70, 72, 73, 74, 77, 79, 80, 84, 85], "branches": [[65, 66], [65, 70], [73, 74], [73, 77]]}
# gained: {"lines": [41, 49, 52, 56, 62, 64, 65, 66, 70, 72, 73, 74, 77, 79, 80, 84, 85], "branches": [[65, 66], [65, 70], [73, 74], [73, 77]]}

import pytest
from flask.sansio.blueprints import Blueprint, BlueprintSetupState
from flask.sansio.app import App

class MockApp:
    """Mock App class to avoid initialization issues"""
    def __init__(self, name):
        self.name = name

class TestBlueprintSetupState:
    def test_init_with_all_options_provided(self):
        """Test BlueprintSetupState initialization with all options provided in options dict."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__)
        
        options = {
            "subdomain": "admin",
            "url_prefix": "/api",
            "name": "custom_name",
            "name_prefix": "prefix_",
            "url_defaults": {"version": "v1"}
        }
        
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.app is app
        assert state.blueprint is blueprint
        assert state.options is options
        assert state.first_registration is True
        assert state.subdomain == "admin"
        assert state.url_prefix == "/api"
        assert state.name == "custom_name"
        assert state.name_prefix == "prefix_"
        assert state.url_defaults == {"version": "v1"}

    def test_init_with_no_options_uses_blueprint_defaults(self):
        """Test BlueprintSetupState initialization with no options, using blueprint defaults."""
        app = MockApp("test_app")
        blueprint = Blueprint(
            "test_bp", 
            __name__, 
            subdomain="api",
            url_prefix="/v1",
            url_defaults={"lang": "en"}
        )
        
        options = {}
        state = BlueprintSetupState(blueprint, app, options, False)
        
        assert state.app is app
        assert state.blueprint is blueprint
        assert state.options is options
        assert state.first_registration is False
        assert state.subdomain == "api"
        assert state.url_prefix == "/v1"
        assert state.name == "test_bp"
        assert state.name_prefix == ""
        assert state.url_defaults == {"lang": "en"}

    def test_init_with_partial_options_mixed_with_blueprint_defaults(self):
        """Test BlueprintSetupState initialization with some options provided, some using blueprint defaults."""
        app = MockApp("test_app")
        blueprint = Blueprint(
            "test_bp", 
            __name__, 
            subdomain="api",
            url_prefix="/v1",
            url_defaults={"lang": "en"}
        )
        
        options = {
            "url_prefix": "/v2",
            "name_prefix": "test_",
            "url_defaults": {"version": "2.0"}
        }
        
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.subdomain == "api"  # from blueprint (not in options)
        assert state.url_prefix == "/v2"  # from options
        assert state.name == "test_bp"  # from blueprint (no name in options)
        assert state.name_prefix == "test_"  # from options
        assert state.url_defaults == {"lang": "en", "version": "2.0"}  # merged

    def test_init_with_none_subdomain_in_options_uses_blueprint(self):
        """Test BlueprintSetupState when subdomain is None in options - should use blueprint subdomain."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__, subdomain="api")
        
        options = {"subdomain": None}
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.subdomain == "api"  # None in options means use blueprint subdomain

    def test_init_with_none_url_prefix_in_options_uses_blueprint(self):
        """Test BlueprintSetupState when url_prefix is None in options - should use blueprint url_prefix."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__, url_prefix="/v1")
        
        options = {"url_prefix": None}
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.url_prefix == "/v1"  # None in options means use blueprint url_prefix

    def test_init_with_empty_url_defaults(self):
        """Test BlueprintSetupState with empty url_defaults in options."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__, url_defaults={"default": "value"})
        
        options = {"url_defaults": {}}
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.url_defaults == {"default": "value"}  # blueprint defaults only

    def test_init_with_tuple_url_defaults(self):
        """Test BlueprintSetupState with url_defaults as tuple in options."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__, url_defaults={"blueprint": "value"})
        
        options = {"url_defaults": (("option", "opt_value"),)}
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.url_defaults == {"blueprint": "value", "option": "opt_value"}

    def test_init_with_no_url_defaults_in_options_or_blueprint(self):
        """Test BlueprintSetupState with no url_defaults in options and empty blueprint defaults."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__)  # No url_defaults provided
        
        options = {}
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.url_defaults == {}  # Empty dict when no defaults anywhere

    def test_init_with_missing_subdomain_options_uses_blueprint(self):
        """Test BlueprintSetupState when subdomain is missing from options - should use blueprint subdomain."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__, subdomain="api")
        
        options = {}  # No subdomain in options
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.subdomain == "api"  # Missing from options means use blueprint subdomain

    def test_init_with_missing_url_prefix_options_uses_blueprint(self):
        """Test BlueprintSetupState when url_prefix is missing from options - should use blueprint url_prefix."""
        app = MockApp("test_app")
        blueprint = Blueprint("test_bp", __name__, url_prefix="/v1")
        
        options = {}  # No url_prefix in options
        state = BlueprintSetupState(blueprint, app, options, True)
        
        assert state.url_prefix == "/v1"  # Missing from options means use blueprint url_prefix
