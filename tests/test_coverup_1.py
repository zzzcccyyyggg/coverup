# file: src/flask/src/flask/sansio/blueprints.py:174-211
# asked: {"lines": [174, 178, 179, 180, 181, 182, 183, 184, 185, 187, 188, 189, 190, 191, 192, 195, 196, 198, 199, 201, 202, 203, 204, 206, 207, 209, 210, 211], "branches": [[195, 196], [195, 198], [198, 199], [198, 201], [206, 207], [206, 209]]}
# gained: {"lines": [174, 178, 179, 180, 181, 182, 183, 184, 185, 187, 188, 189, 190, 191, 192, 195, 196, 198, 199, 201, 202, 203, 204, 206, 207, 209, 210, 211], "branches": [[195, 196], [195, 198], [198, 199], [198, 201], [206, 207], [206, 209]]}

import pytest
from flask.sansio.blueprints import Blueprint
from flask.sansio.scaffold import _sentinel

class TestBlueprintInit:
    """Test cases for Blueprint.__init__ method to cover lines 174-211."""
    
    def test_init_with_empty_name_raises_value_error(self):
        """Test that empty name raises ValueError (line 195-196)."""
        with pytest.raises(ValueError, match="'name' may not be empty."):
            Blueprint(name="", import_name="test")
    
    def test_init_with_dot_in_name_raises_value_error(self):
        """Test that name with dot raises ValueError (line 198-199)."""
        with pytest.raises(ValueError, match="'name' may not contain a dot '.' character."):
            Blueprint(name="test.blueprint", import_name="test")
    
    def test_init_with_valid_name_and_defaults(self):
        """Test initialization with valid name and default parameters (lines 201-211)."""
        bp = Blueprint(name="test", import_name="test")
        
        assert bp.name == "test"
        assert bp.url_prefix is None
        assert bp.subdomain is None
        assert bp.deferred_functions == []
        assert bp.url_values_defaults == {}
        assert bp.cli_group is _sentinel
        assert bp._blueprints == []
    
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters (lines 201-211)."""
        bp = Blueprint(
            name="test",
            import_name="test",
            static_folder="static",
            static_url_path="/static",
            template_folder="templates",
            url_prefix="/api",
            subdomain="api",
            url_defaults={"version": "v1"},
            root_path="/some/path",
            cli_group="test_group"
        )
        
        assert bp.name == "test"
        assert bp.url_prefix == "/api"
        assert bp.subdomain == "api"
        assert bp.deferred_functions == []
        assert bp.url_values_defaults == {"version": "v1"}
        assert bp.cli_group == "test_group"
        assert bp._blueprints == []
    
    def test_init_with_none_url_defaults(self):
        """Test initialization with None url_defaults (lines 206-209)."""
        bp = Blueprint(
            name="test",
            import_name="test",
            url_defaults=None
        )
        
        assert bp.url_values_defaults == {}
