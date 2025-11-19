# file: src/flask/src/flask/sansio/app.py:559-564
# asked: {"lines": [559, 560, 561, 563, 564], "branches": [[563, 0], [563, 564]]}
# gained: {"lines": [559, 560, 561, 563, 564], "branches": [[563, 0], [563, 564]]}

import pytest
from flask import Flask

class TestAppDebugSetter:
    def test_debug_setter_with_templates_auto_reload_none(self, monkeypatch):
        """Test that when TEMPLATES_AUTO_RELOAD is None, jinja_env.auto_reload is set to the debug value."""
        app = Flask(__name__)
        
        # Set TEMPLATES_AUTO_RELOAD to None to trigger the condition
        app.config["TEMPLATES_AUTO_RELOAD"] = None
        
        # Mock the jinja_env to verify auto_reload is set
        mock_jinja_env = type('MockJinjaEnv', (), {'auto_reload': None})()
        monkeypatch.setattr(app, 'jinja_env', mock_jinja_env)
        
        # Set debug to True - this should set jinja_env.auto_reload to True
        app.debug = True
        assert app.config["DEBUG"] is True
        assert mock_jinja_env.auto_reload is True
        
        # Set debug to False - this should set jinja_env.auto_reload to False
        app.debug = False
        assert app.config["DEBUG"] is False
        assert mock_jinja_env.auto_reload is False

    def test_debug_setter_with_templates_auto_reload_set(self):
        """Test that when TEMPLATES_AUTO_RELOAD is already set, jinja_env.auto_reload is not modified."""
        app = Flask(__name__)
        
        # Set TEMPLATES_AUTO_RELOAD to a specific value (not None)
        app.config["TEMPLATES_AUTO_RELOAD"] = False
        
        # Store original auto_reload value
        original_auto_reload = app.jinja_env.auto_reload
        
        # Set debug to True - this should NOT modify jinja_env.auto_reload
        app.debug = True
        assert app.config["DEBUG"] is True
        assert app.jinja_env.auto_reload == original_auto_reload
        
        # Set debug to False - this should NOT modify jinja_env.auto_reload
        app.debug = False
        assert app.config["DEBUG"] is False
        assert app.jinja_env.auto_reload == original_auto_reload
