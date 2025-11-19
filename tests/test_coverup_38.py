# file: src/flask/src/flask/app.py:221-274
# asked: {"lines": [221, 224, 225, 226, 227, 228, 229, 230, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 251, 255, 262, 263, 264, 268, 269, 270, 271, 272, 273], "branches": [[262, 0], [262, 263]]}
# gained: {"lines": [221, 224, 225, 226, 227, 228, 229, 230, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 251, 255, 262, 263, 264, 268, 269, 270, 271, 272, 273], "branches": [[262, 0], [262, 263]]}

import pytest
import tempfile
import os
from flask import Flask

class TestFlaskInit:
    """Test cases for Flask.__init__ method to cover lines 221-273"""
    
    def test_flask_init_with_static_folder_and_host_matching(self):
        """Test Flask initialization with static_folder and host_matching=True, static_host provided"""
        # This should trigger the static route creation with host matching
        app = Flask(
            __name__,
            static_folder="static",
            host_matching=True,
            static_host="example.com"
        )
        
        # Verify CLI group is set up
        assert hasattr(app, 'cli')
        assert app.cli.name == app.name
        
        # Verify static route was added
        assert len(app.url_map._rules) > 0
        static_rule = None
        for rule in app.url_map._rules:
            if rule.endpoint == 'static':
                static_rule = rule
                break
        assert static_rule is not None
        assert static_rule.host == "example.com"
        assert static_rule.rule == "/static/<path:filename>"
    
    def test_flask_init_with_static_folder_no_host_matching(self):
        """Test Flask initialization with static_folder but no host matching"""
        # This should trigger the static route creation without host matching
        app = Flask(
            __name__,
            static_folder="static",
            host_matching=False,
            static_host=None
        )
        
        # Verify CLI group is set up
        assert hasattr(app, 'cli')
        assert app.cli.name == app.name
        
        # Verify static route was added
        assert len(app.url_map._rules) > 0
        static_rule = None
        for rule in app.url_map._rules:
            if rule.endpoint == 'static':
                static_rule = rule
                break
        assert static_rule is not None
        assert static_rule.host is None
        assert static_rule.rule == "/static/<path:filename>"
    
    def test_flask_init_without_static_folder(self):
        """Test Flask initialization without static_folder (should not add static route)"""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Flask app without static_folder
            app = Flask(
                __name__,
                static_folder=None,
                root_path=temp_dir
            )
            
            # Verify CLI group is set up
            assert hasattr(app, 'cli')
            assert app.cli.name == app.name
            
            # Verify no static route was added
            static_rules = [rule for rule in app.url_map._rules if rule.endpoint == 'static']
            assert len(static_rules) == 0
    
    def test_flask_init_invalid_static_host_host_matching_combination(self):
        """Test that Flask raises AssertionError for invalid static_host/host_matching combination"""
        # Test case 1: host_matching=True but static_host=None
        with pytest.raises(AssertionError, match="Invalid static_host/host_matching combination"):
            Flask(
                __name__,
                static_folder="static",
                host_matching=True,
                static_host=None
            )
        
        # Test case 2: host_matching=False but static_host is provided
        with pytest.raises(AssertionError, match="Invalid static_host/host_matching combination"):
            Flask(
                __name__,
                static_folder="static",
                host_matching=False,
                static_host="example.com"
            )
    
    def test_flask_init_with_custom_static_url_path(self):
        """Test Flask initialization with custom static_url_path"""
        app = Flask(
            __name__,
            static_folder="static",
            static_url_path="/assets"
        )
        
        # Verify CLI group is set up
        assert hasattr(app, 'cli')
        assert app.cli.name == app.name
        
        # Verify static route was added with custom path
        assert len(app.url_map._rules) > 0
        static_rule = None
        for rule in app.url_map._rules:
            if rule.endpoint == 'static':
                static_rule = rule
                break
        assert static_rule is not None
        assert static_rule.rule == "/assets/<path:filename>"
    
    def test_flask_init_with_non_default_parameters(self):
        """Test Flask initialization with various non-default parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create instance path
            instance_path = os.path.join(temp_dir, "instance")
            os.makedirs(instance_path)
            
            # Create static folder
            static_folder = os.path.join(temp_dir, "custom_static")
            os.makedirs(static_folder)
            
            # Create template folder
            template_folder = os.path.join(temp_dir, "custom_templates")
            os.makedirs(template_folder)
            
            app = Flask(
                __name__,
                static_url_path="/custom_static",
                static_folder=static_folder,
                static_host=None,
                host_matching=False,
                subdomain_matching=True,
                template_folder=template_folder,
                instance_path=instance_path,
                instance_relative_config=True,
                root_path=temp_dir
            )
            
            # Verify CLI group is set up
            assert hasattr(app, 'cli')
            assert app.cli.name == app.name
            
            # Verify static route was added with custom path
            assert len(app.url_map._rules) > 0
            static_rule = None
            for rule in app.url_map._rules:
                if rule.endpoint == 'static':
                    static_rule = rule
                    break
            assert static_rule is not None
            assert static_rule.rule == "/custom_static/<path:filename>"
            
            # Verify other properties
            assert app.static_folder == static_folder
            assert app.template_folder == template_folder
            assert app.instance_path == instance_path
            assert app.subdomain_matching == True
            # instance_relative_config is used internally by config, not exposed as attribute
            # We can verify it worked by checking the config behavior
            assert hasattr(app, 'config')
