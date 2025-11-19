# file: src/flask/src/flask/sansio/blueprints.py:246-253
# asked: {"lines": [246, 247, 253], "branches": []}
# gained: {"lines": [246, 247, 253], "branches": []}

import pytest
from unittest.mock import Mock, patch
from flask.sansio.blueprints import Blueprint, BlueprintSetupState
from flask.sansio.app import App

class TestBlueprintMakeSetupState:
    def test_make_setup_state_creates_blueprint_setup_state(self):
        """Test that make_setup_state returns a BlueprintSetupState instance."""
        with patch.object(App, 'make_config', return_value=Mock()):
            app = App(__name__)
            blueprint = Blueprint('test_blueprint', __name__)
            options = {'url_prefix': '/test'}
            
            setup_state = blueprint.make_setup_state(app, options)
            
            assert isinstance(setup_state, BlueprintSetupState)
            assert setup_state.blueprint == blueprint
            assert setup_state.app == app
            assert setup_state.options == options
            assert setup_state.first_registration is False

    def test_make_setup_state_with_first_registration_true(self):
        """Test that make_setup_state passes first_registration parameter correctly."""
        with patch.object(App, 'make_config', return_value=Mock()):
            app = App(__name__)
            blueprint = Blueprint('test_blueprint', __name__)
            options = {'name_prefix': 'test_'}
            
            setup_state = blueprint.make_setup_state(app, options, first_registration=True)
            
            assert isinstance(setup_state, BlueprintSetupState)
            assert setup_state.blueprint == blueprint
            assert setup_state.app == app
            assert setup_state.options == options
            assert setup_state.first_registration is True

    def test_make_setup_state_with_empty_options(self):
        """Test that make_setup_state works with empty options dictionary."""
        with patch.object(App, 'make_config', return_value=Mock()):
            app = App(__name__)
            blueprint = Blueprint('test_blueprint', __name__)
            options = {}
            
            setup_state = blueprint.make_setup_state(app, options)
            
            assert isinstance(setup_state, BlueprintSetupState)
            assert setup_state.blueprint == blueprint
            assert setup_state.app == app
            assert setup_state.options == options
            assert setup_state.first_registration is False
