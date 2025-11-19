# file: src/flask/src/flask/app.py:380-418
# asked: {"lines": [380, 392, 394, 395, 397, 398, 400, 401, 403, 405, 406, 407, 408, 409, 413, 414, 415, 417, 418], "branches": [[394, 395], [394, 397], [397, 398], [397, 405], [400, 401], [400, 403]]}
# gained: {"lines": [380, 392, 394, 395, 397, 398, 400, 401, 403, 405, 406, 407, 408, 409, 413, 414, 415, 417, 418], "branches": [[394, 395], [394, 397], [397, 398], [397, 405], [400, 401], [400, 403]]}

import pytest
from flask import Flask
from flask.templating import Environment
from unittest.mock import Mock, patch


class TestFlaskCreateJinjaEnvironment:
    """Test cases for Flask.create_jinja_environment method to achieve full coverage."""
    
    def test_create_jinja_environment_without_autoescape_in_options(self):
        """Test when 'autoescape' is not in jinja_options."""
        app = Flask(__name__)
        app.jinja_options = {}
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        # The autoescape option should be set to the select_jinja_autoescape method
        # We can't test identity directly, but we can verify the function exists
        assert callable(env.autoescape)
    
    def test_create_jinja_environment_with_autoescape_in_options(self):
        """Test when 'autoescape' is already in jinja_options."""
        app = Flask(__name__)
        app.jinja_options = {'autoescape': False}
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        assert env.autoescape is False
    
    def test_create_jinja_environment_without_auto_reload_in_options(self):
        """Test when 'auto_reload' is not in jinja_options."""
        app = Flask(__name__)
        app.jinja_options = {}
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.debug = False
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        assert env.auto_reload is True
    
    def test_create_jinja_environment_with_auto_reload_in_options(self):
        """Test when 'auto_reload' is already in jinja_options."""
        app = Flask(__name__)
        app.jinja_options = {'auto_reload': False}
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        assert env.auto_reload is False
    
    def test_create_jinja_environment_auto_reload_none_with_debug_true(self):
        """Test when TEMPLATES_AUTO_RELOAD is None and debug is True."""
        app = Flask(__name__)
        app.jinja_options = {}
        app.config['TEMPLATES_AUTO_RELOAD'] = None
        app.debug = True
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        assert env.auto_reload is True
    
    def test_create_jinja_environment_auto_reload_none_with_debug_false(self):
        """Test when TEMPLATES_AUTO_RELOAD is None and debug is False."""
        app = Flask(__name__)
        app.jinja_options = {}
        app.config['TEMPLATES_AUTO_RELOAD'] = None
        app.debug = False
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        assert env.auto_reload is False
    
    def test_create_jinja_environment_globals_are_set(self):
        """Test that Flask globals are properly set in the Jinja environment."""
        app = Flask(__name__)
        app.jinja_options = {}
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        assert 'url_for' in env.globals
        assert 'get_flashed_messages' in env.globals
        assert 'config' in env.globals
        assert 'request' in env.globals
        assert 'session' in env.globals
        assert 'g' in env.globals
        assert env.globals['config'] is app.config
        # Don't test identity for bound methods, just check they exist
        assert callable(env.globals['url_for'])
    
    def test_create_jinja_environment_json_policy_is_set(self):
        """Test that JSON dumps policy is properly set."""
        app = Flask(__name__)
        app.jinja_options = {}
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        env = app.create_jinja_environment()
        
        assert isinstance(env, Environment)
        assert 'json.dumps_function' in env.policies
        # Don't test identity for bound methods, just check it's callable
        assert callable(env.policies['json.dumps_function'])
    
    def test_create_jinja_environment_with_custom_jinja_environment(self):
        """Test with a custom jinja_environment class."""
        app = Flask(__name__)
        app.jinja_options = {}
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        # Mock the jinja_environment to verify it's called with correct parameters
        with patch.object(app, 'jinja_environment') as mock_env:
            mock_env.return_value = Mock(spec=Environment)
            mock_env.return_value.globals = {}
            mock_env.return_value.policies = {}
            
            env = app.create_jinja_environment()
            
            # Verify the mock was called with the app instance and options
            mock_env.assert_called_once()
            call_args = mock_env.call_args
            assert call_args[0][0] is app  # First positional arg should be the app
            assert 'autoescape' in call_args[1]
            assert 'auto_reload' in call_args[1]
            assert env is mock_env.return_value
    
    def test_create_jinja_environment_verifies_options_passed_to_jinja(self):
        """Test that the options dict is properly constructed and passed to jinja_environment."""
        app = Flask(__name__)
        app.jinja_options = {'custom_option': 'custom_value'}
        app.config['TEMPLATES_AUTO_RELOAD'] = False
        app.debug = True
        
        with patch.object(app, 'jinja_environment') as mock_env:
            mock_env.return_value = Mock(spec=Environment)
            mock_env.return_value.globals = {}
            mock_env.return_value.policies = {}
            
            env = app.create_jinja_environment()
            
            # Check that custom options are preserved
            call_kwargs = mock_env.call_args[1]
            assert call_kwargs['custom_option'] == 'custom_value'
            # autoescape should be added since it wasn't in jinja_options
            assert 'autoescape' in call_kwargs
            # auto_reload should be False from config
            assert call_kwargs['auto_reload'] is False
